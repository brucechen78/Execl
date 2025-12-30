import os
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import openpyxl
import xlrd

from ..database import get_db
from ..config import MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from .. import crud, schemas

router = APIRouter(prefix="/api", tags=["excel"])


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


def parse_xlsx(file_data: bytes) -> List[dict]:
    """解析.xlsx文件"""
    workbook = openpyxl.load_workbook(BytesIO(file_data), read_only=True, data_only=True)
    sheets_data = []

    for idx, sheet_name in enumerate(workbook.sheetnames):
        sheet = workbook[sheet_name]
        rows = list(sheet.iter_rows(values_only=True))

        # 计算实际行列数
        row_count = len(rows)
        column_count = max((len(row) for row in rows), default=0) if rows else 0

        # 收集单元格数据
        cells = []
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                if value is not None:
                    cells.append((row_idx, col_idx, value))

        sheets_data.append({
            "name": sheet_name,
            "index": idx,
            "row_count": row_count,
            "column_count": column_count,
            "cells": cells
        })

    workbook.close()
    return sheets_data


def parse_xls(file_data: bytes) -> List[dict]:
    """解析.xls文件"""
    workbook = xlrd.open_workbook(file_contents=file_data)
    sheets_data = []

    for idx in range(workbook.nsheets):
        sheet = workbook.sheet_by_index(idx)

        # 收集单元格数据
        cells = []
        for row_idx in range(sheet.nrows):
            for col_idx in range(sheet.ncols):
                value = sheet.cell_value(row_idx, col_idx)
                if value != "":
                    cells.append((row_idx, col_idx, value))

        sheets_data.append({
            "name": sheet.name,
            "index": idx,
            "row_count": sheet.nrows,
            "column_count": sheet.ncols,
            "cells": cells
        })

    return sheets_data


@router.post("/upload", response_model=schemas.UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传Excel文件"""
    # 检查文件扩展名
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}")

    # 读取文件内容
    file_data = await file.read()
    file_size = len(file_data)

    # 检查文件大小
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超出限制（最大{MAX_FILE_SIZE // 1024 // 1024}MB）")

    # 解析Excel
    try:
        if ext == ".xlsx":
            sheets_data = parse_xlsx(file_data)
        else:
            sheets_data = parse_xls(file_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel文件解析失败: {str(e)}")

    # 保存文件信息
    db_file = crud.create_excel_file(
        db=db,
        filename=file.filename,
        file_data=file_data,
        file_size=file_size,
        sheet_count=len(sheets_data)
    )

    # 保存Sheet和数据
    for sheet_info in sheets_data:
        db_sheet = crud.create_excel_sheet(
            db=db,
            file_id=db_file.id,
            sheet_name=sheet_info["name"],
            sheet_index=sheet_info["index"],
            row_count=sheet_info["row_count"],
            column_count=sheet_info["column_count"]
        )

        # 批量保存单元格数据
        if sheet_info["cells"]:
            crud.bulk_create_excel_data(db, db_sheet.id, sheet_info["cells"])

    return schemas.UploadResponse(
        id=db_file.id,
        filename=db_file.filename,
        message="上传成功"
    )


@router.get("/files", response_model=schemas.FileListResponse)
def get_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取文件列表"""
    total, files = crud.get_files(db, skip=skip, limit=limit)
    return schemas.FileListResponse(
        total=total,
        items=[schemas.FileInfo.model_validate(f) for f in files]
    )


@router.get("/files/{file_id}", response_model=schemas.FileDetail)
def get_file_detail(file_id: int, db: Session = Depends(get_db)):
    """获取文件详情（包含Sheet列表）"""
    db_file = crud.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")
    return schemas.FileDetail.model_validate(db_file)


@router.get("/files/{file_id}/sheets/{sheet_id}/data", response_model=schemas.SheetDataResponse)
def get_sheet_data(
    file_id: int,
    sheet_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取Sheet数据（分页）"""
    # 验证文件存在
    db_file = crud.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 验证Sheet存在且属于该文件
    db_sheet = crud.get_sheet_by_id(db, sheet_id)
    if not db_sheet or db_sheet.file_id != file_id:
        raise HTTPException(status_code=404, detail="Sheet不存在")

    # 获取分页数据
    data_records, total_rows = crud.get_sheet_data(db, sheet_id, page, page_size)

    # 将数据转换为二维数组格式
    # 首先确定列数
    column_count = db_sheet.column_count

    # 生成表头（第一行数据或列索引）
    headers = []
    if total_rows > 0:
        # 获取第一行作为表头
        header_cells = {d.column_index: d.cell_value for d in data_records if d.row_index == 0}
        if header_cells:
            headers = [header_cells.get(i, f"列{i+1}") or f"列{i+1}" for i in range(column_count)]
        else:
            headers = [f"列{i+1}" for i in range(column_count)]
    else:
        headers = [f"列{i+1}" for i in range(column_count)]

    # 组织数据为二维数组
    data_dict = {}
    for record in data_records:
        if record.row_index not in data_dict:
            data_dict[record.row_index] = {}
        data_dict[record.row_index][record.column_index] = record.cell_value

    # 转换为列表格式
    rows = []
    start_row = (page - 1) * page_size
    for row_idx in range(start_row, min(start_row + page_size, total_rows + 1)):
        if row_idx in data_dict:
            row = [data_dict[row_idx].get(col_idx, "") for col_idx in range(column_count)]
            rows.append(row)

    return schemas.SheetDataResponse(
        sheet_id=sheet_id,
        sheet_name=db_sheet.sheet_name,
        total_rows=total_rows + 1,  # 包含表头行
        total_columns=column_count,
        page=page,
        page_size=page_size,
        headers=headers,
        data=rows
    )


@router.get("/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    """下载原始Excel文件"""
    db_file = crud.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 确定Content-Type
    ext = get_file_extension(db_file.filename)
    if ext == ".xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        media_type = "application/vnd.ms-excel"

    return StreamingResponse(
        BytesIO(db_file.file_data),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{db_file.filename}"'
        }
    )


@router.delete("/files/{file_id}", response_model=schemas.MessageResponse)
def delete_file(file_id: int, db: Session = Depends(get_db)):
    """删除文件"""
    if not crud.delete_file(db, file_id):
        raise HTTPException(status_code=404, detail="文件不存在")
    return schemas.MessageResponse(message="删除成功")
