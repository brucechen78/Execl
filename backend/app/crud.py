from typing import List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models


def create_excel_file(
    db: Session,
    filename: str,
    file_data: bytes,
    file_size: int,
    sheet_count: int
) -> models.ExcelFile:
    """创建Excel文件记录"""
    db_file = models.ExcelFile(
        filename=filename,
        file_data=file_data,
        file_size=file_size,
        sheet_count=sheet_count
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def create_excel_sheet(
    db: Session,
    file_id: int,
    sheet_name: str,
    sheet_index: int,
    row_count: int,
    column_count: int
) -> models.ExcelSheet:
    """创建Sheet记录"""
    db_sheet = models.ExcelSheet(
        file_id=file_id,
        sheet_name=sheet_name,
        sheet_index=sheet_index,
        row_count=row_count,
        column_count=column_count
    )
    db.add(db_sheet)
    db.commit()
    db.refresh(db_sheet)
    return db_sheet


def bulk_create_excel_data(
    db: Session,
    sheet_id: int,
    data: List[Tuple[int, int, Any]]
) -> None:
    """批量创建单元格数据"""
    db_data_list = [
        models.ExcelData(
            sheet_id=sheet_id,
            row_index=row_idx,
            column_index=col_idx,
            cell_value=str(value) if value is not None else None
        )
        for row_idx, col_idx, value in data
    ]
    db.bulk_save_objects(db_data_list)
    db.commit()


def get_files(db: Session, skip: int = 0, limit: int = 100) -> Tuple[int, List[models.ExcelFile]]:
    """获取文件列表"""
    total = db.query(func.count(models.ExcelFile.id)).scalar()
    files = db.query(models.ExcelFile).order_by(
        models.ExcelFile.created_at.desc()
    ).offset(skip).limit(limit).all()
    return total, files


def get_file_by_id(db: Session, file_id: int) -> Optional[models.ExcelFile]:
    """根据ID获取文件"""
    return db.query(models.ExcelFile).filter(models.ExcelFile.id == file_id).first()


def get_sheet_by_id(db: Session, sheet_id: int) -> Optional[models.ExcelSheet]:
    """根据ID获取Sheet"""
    return db.query(models.ExcelSheet).filter(models.ExcelSheet.id == sheet_id).first()


def get_sheet_data(
    db: Session,
    sheet_id: int,
    page: int = 1,
    page_size: int = 50
) -> Tuple[List[models.ExcelData], int]:
    """获取Sheet数据（分页）"""
    # 计算总行数
    total_rows = db.query(func.max(models.ExcelData.row_index)).filter(
        models.ExcelData.sheet_id == sheet_id
    ).scalar() or 0

    # 计算分页的行范围
    start_row = (page - 1) * page_size
    end_row = start_row + page_size

    # 查询指定行范围的数据
    data = db.query(models.ExcelData).filter(
        models.ExcelData.sheet_id == sheet_id,
        models.ExcelData.row_index >= start_row,
        models.ExcelData.row_index < end_row
    ).order_by(
        models.ExcelData.row_index,
        models.ExcelData.column_index
    ).all()

    return data, total_rows


def delete_file(db: Session, file_id: int) -> bool:
    """删除文件（级联删除Sheet和数据）"""
    db_file = get_file_by_id(db, file_id)
    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    return False
