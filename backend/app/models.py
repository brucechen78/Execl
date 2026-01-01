from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, LargeBinary, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)

    # 关系
    excel_files = relationship("ExcelFile", back_populates="user")


class Session(Base):
    """会话表"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                      nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False, index=True)

    # 关系
    user = relationship("User")


class ExcelFile(Base):
    """Excel文件信息表"""
    __tablename__ = "excel_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_data = Column(LargeBinary(length=2**32-1), nullable=False, comment="文件二进制数据")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    sheet_count = Column(Integer, nullable=False, default=0, comment="Sheet数量")
    created_at = Column(DateTime, server_default=func.now(), comment="上传时间")

    # 关联Sheet
    sheets = relationship("ExcelSheet", back_populates="file", cascade="all, delete-orphan")
    # 关联User
    user = relationship("User", back_populates="excel_files")


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
    merged_cells = relationship("MergedCell", back_populates="sheet", cascade="all, delete-orphan")
    images = relationship("SheetImage", back_populates="sheet", cascade="all, delete-orphan")
    charts = relationship("SheetChart", back_populates="sheet", cascade="all, delete-orphan")
    table_regions = relationship("TableRegion", back_populates="sheet", cascade="all, delete-orphan")


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


class MergedCell(Base):
    """合并单元格信息表"""
    __tablename__ = "merged_cells"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    sheet_id = Column(Integer, ForeignKey("excel_sheets.id", ondelete="CASCADE"), nullable=False, index=True)
    start_row = Column(Integer, nullable=False, comment="起始行号")
    start_col = Column(Integer, nullable=False, comment="起始列号")
    end_row = Column(Integer, nullable=False, comment="结束行号")
    end_col = Column(Integer, nullable=False, comment="结束列号")

    # 关联
    sheet = relationship("ExcelSheet", back_populates="merged_cells")


class SheetImage(Base):
    """Sheet内嵌图片表"""
    __tablename__ = "sheet_images"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    sheet_id = Column(Integer, ForeignKey("excel_sheets.id", ondelete="CASCADE"), nullable=False, index=True)
    image_data = Column(LargeBinary(length=2**24-1), nullable=False, comment="图片二进制数据")
    image_format = Column(String(20), nullable=False, comment="图片格式(png/jpeg/gif等)")
    anchor_type = Column(String(20), nullable=False, default="oneCellAnchor", comment="锚定类型")
    anchor_row = Column(Integer, nullable=False, comment="锚定行号")
    anchor_col = Column(Integer, nullable=False, comment="锚定列号")
    width = Column(Integer, nullable=True, comment="图片宽度(像素)")
    height = Column(Integer, nullable=True, comment="图片高度(像素)")

    # 关联
    sheet = relationship("ExcelSheet", back_populates="images")


class SheetChart(Base):
    """Sheet内嵌图表表"""
    __tablename__ = "sheet_charts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    sheet_id = Column(Integer, ForeignKey("excel_sheets.id", ondelete="CASCADE"), nullable=False, index=True)
    chart_type = Column(String(50), nullable=False, comment="图表类型")
    chart_title = Column(String(255), nullable=True, comment="图表标题")
    chart_data = Column(JSON, nullable=True, comment="图表数据(JSON格式)")
    anchor_row = Column(Integer, nullable=False, comment="锚定行号")
    anchor_col = Column(Integer, nullable=False, comment="锚定列号")
    width = Column(Integer, nullable=True, comment="图表宽度")
    height = Column(Integer, nullable=True, comment="图表高度")

    # 关联
    sheet = relationship("ExcelSheet", back_populates="charts")


class TableRegion(Base):
    """Sheet内表格区域表(支持单个Sheet多表头表格)"""
    __tablename__ = "table_regions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    sheet_id = Column(Integer, ForeignKey("excel_sheets.id", ondelete="CASCADE"), nullable=False, index=True)
    region_index = Column(Integer, nullable=False, comment="区域序号")
    start_row = Column(Integer, nullable=False, comment="起始行号")
    start_col = Column(Integer, nullable=False, comment="起始列号")
    end_row = Column(Integer, nullable=False, comment="结束行号")
    end_col = Column(Integer, nullable=False, comment="结束列号")
    header_rows = Column(Integer, nullable=False, default=1, comment="表头行数")
    table_name = Column(String(255), nullable=True, comment="表格名称(可选)")

    # 关联
    sheet = relationship("ExcelSheet", back_populates="table_regions")
