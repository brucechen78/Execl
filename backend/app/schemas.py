from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel


class MergedCellInfo(BaseModel):
    """合并单元格信息"""
    start_row: int
    start_col: int
    end_row: int
    end_col: int

    class Config:
        from_attributes = True


class ImageInfo(BaseModel):
    """图片信息"""
    id: int
    image_format: str
    anchor_row: int
    anchor_col: int
    width: Optional[int] = None
    height: Optional[int] = None

    class Config:
        from_attributes = True


class ChartInfo(BaseModel):
    """图表信息"""
    id: int
    chart_type: str
    chart_title: Optional[str] = None
    chart_data: Optional[dict] = None
    anchor_row: int
    anchor_col: int
    width: Optional[int] = None
    height: Optional[int] = None

    class Config:
        from_attributes = True


class TableRegionInfo(BaseModel):
    """表格区域信息"""
    id: int
    region_index: int
    start_row: int
    start_col: int
    end_row: int
    end_col: int
    header_rows: int
    table_name: Optional[str] = None

    class Config:
        from_attributes = True


class SheetBase(BaseModel):
    """Sheet基础模型"""
    sheet_name: str
    sheet_index: int
    row_count: int
    column_count: int


class SheetInfo(SheetBase):
    """Sheet信息响应模型"""
    id: int

    class Config:
        from_attributes = True


class FileBase(BaseModel):
    """文件基础模型"""
    filename: str
    file_size: int
    sheet_count: int


class FileInfo(FileBase):
    """文件信息响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FileDetail(FileInfo):
    """文件详情响应模型（包含Sheet列表）"""
    sheets: List[SheetInfo]

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """文件列表响应"""
    total: int
    items: List[FileInfo]


class SheetDataResponse(BaseModel):
    """Sheet数据响应"""
    sheet_id: int
    sheet_name: str
    total_rows: int
    total_columns: int
    page: int
    page_size: int
    headers: List[str]
    data: List[List[Any]]
    merged_cells: List[MergedCellInfo] = []
    images: List[ImageInfo] = []
    charts: List[ChartInfo] = []
    table_regions: List[TableRegionInfo] = []


class UploadResponse(BaseModel):
    """上传响应"""
    id: int
    filename: str
    message: str


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
