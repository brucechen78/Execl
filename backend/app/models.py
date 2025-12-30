from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class ExcelFile(Base):
    """Excel文件信息表"""
    __tablename__ = "excel_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_data = Column(LargeBinary(length=2**32-1), nullable=False, comment="文件二进制数据")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    sheet_count = Column(Integer, nullable=False, default=0, comment="Sheet数量")
    created_at = Column(DateTime, server_default=func.now(), comment="上传时间")

    # 关联Sheet
    sheets = relationship("ExcelSheet", back_populates="file", cascade="all, delete-orphan")


class ExcelSheet(Base):
    """Excel Sheet信息表"""
    __tablename__ = "excel_sheets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("excel_files.id", ondelete="CASCADE"), nullable=False)
    sheet_name = Column(String(255), nullable=False, comment="Sheet名称")
    sheet_index = Column(Integer, nullable=False, comment="Sheet序号")
    row_count = Column(Integer, nullable=False, default=0, comment="行数")
    column_count = Column(Integer, nullable=False, default=0, comment="列数")

    # 关联
    file = relationship("ExcelFile", back_populates="sheets")
    data = relationship("ExcelData", back_populates="sheet", cascade="all, delete-orphan")


class ExcelData(Base):
    """Excel单元格数据表"""
    __tablename__ = "excel_data"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    sheet_id = Column(Integer, ForeignKey("excel_sheets.id", ondelete="CASCADE"), nullable=False, index=True)
    row_index = Column(Integer, nullable=False, comment="行号")
    column_index = Column(Integer, nullable=False, comment="列号")
    cell_value = Column(Text, nullable=True, comment="单元格值")

    # 关联
    sheet = relationship("ExcelSheet", back_populates="data")
