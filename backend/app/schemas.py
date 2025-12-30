from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel


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


class UploadResponse(BaseModel):
    """上传响应"""
    id: int
    filename: str
    message: str


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
