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


def bulk_create_merged_cells(
    db: Session,
    sheet_id: int,
    merged_cells: List[Tuple[int, int, int, int]]
) -> None:
    """批量创建合并单元格记录"""
    if not merged_cells:
        return
    db_merged_list = [
        models.MergedCell(
            sheet_id=sheet_id,
            start_row=start_row,
            start_col=start_col,
            end_row=end_row,
            end_col=end_col
        )
        for start_row, start_col, end_row, end_col in merged_cells
    ]
    db.bulk_save_objects(db_merged_list)
    db.commit()


def create_sheet_image(
    db: Session,
    sheet_id: int,
    image_data: bytes,
    image_format: str,
    anchor_row: int,
    anchor_col: int,
    width: int = None,
    height: int = None,
    anchor_type: str = "oneCellAnchor"
) -> models.SheetImage:
    """创建图片记录"""
    db_image = models.SheetImage(
        sheet_id=sheet_id,
        image_data=image_data,
        image_format=image_format,
        anchor_type=anchor_type,
        anchor_row=anchor_row,
        anchor_col=anchor_col,
        width=width,
        height=height
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def create_sheet_chart(
    db: Session,
    sheet_id: int,
    chart_type: str,
    anchor_row: int,
    anchor_col: int,
    chart_title: str = None,
    chart_data: dict = None,
    width: int = None,
    height: int = None
) -> models.SheetChart:
    """创建图表记录"""
    db_chart = models.SheetChart(
        sheet_id=sheet_id,
        chart_type=chart_type,
        chart_title=chart_title,
        chart_data=chart_data,
        anchor_row=anchor_row,
        anchor_col=anchor_col,
        width=width,
        height=height
    )
    db.add(db_chart)
    db.commit()
    db.refresh(db_chart)
    return db_chart


def bulk_create_table_regions(
    db: Session,
    sheet_id: int,
    regions: List[Tuple[int, int, int, int, int, int, str]]
) -> None:
    """批量创建表格区域记录
    regions: List of (region_index, start_row, start_col, end_row, end_col, header_rows, table_name)
    """
    if not regions:
        return
    db_regions = [
        models.TableRegion(
            sheet_id=sheet_id,
            region_index=region_index,
            start_row=start_row,
            start_col=start_col,
            end_row=end_row,
            end_col=end_col,
            header_rows=header_rows,
            table_name=table_name
        )
        for region_index, start_row, start_col, end_row, end_col, header_rows, table_name in regions
    ]
    db.bulk_save_objects(db_regions)
    db.commit()


def get_sheet_merged_cells(db: Session, sheet_id: int) -> List[models.MergedCell]:
    """获取Sheet的所有合并单元格"""
    return db.query(models.MergedCell).filter(
        models.MergedCell.sheet_id == sheet_id
    ).all()


def get_sheet_images(db: Session, sheet_id: int) -> List[models.SheetImage]:
    """获取Sheet的所有图片"""
    return db.query(models.SheetImage).filter(
        models.SheetImage.sheet_id == sheet_id
    ).all()


def get_sheet_image_by_id(db: Session, image_id: int) -> Optional[models.SheetImage]:
    """根据ID获取图片"""
    return db.query(models.SheetImage).filter(models.SheetImage.id == image_id).first()


def get_sheet_charts(db: Session, sheet_id: int) -> List[models.SheetChart]:
    """获取Sheet的所有图表"""
    return db.query(models.SheetChart).filter(
        models.SheetChart.sheet_id == sheet_id
    ).all()


def get_sheet_table_regions(db: Session, sheet_id: int) -> List[models.TableRegion]:
    """获取Sheet的所有表格区域"""
    return db.query(models.TableRegion).filter(
        models.TableRegion.sheet_id == sheet_id
    ).order_by(models.TableRegion.region_index).all()
