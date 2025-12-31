# Excel 文件管理系统

一个基于 Web 的 Excel 文件管理系统，支持上传、存储、查看、下载和删除 Excel 文件。

## 功能特性

- **文件上传**：支持 .xls 和 .xlsx 格式，拖拽或点击上传
- **文件存储**：原始文件二进制存储 + 解析数据结构化存储
- **数据展示**：表格形式展示，支持分页和多 Sheet 切换
- **文件下载**：下载原始 Excel 文件
- **文件删除**：删除文件及关联数据
- **合并单元格**：正确解析和渲染 Excel 中的合并单元格
- **内嵌图片**：提取并展示 Excel 中的图片，支持点击预览
- **内嵌图表**：识别图表类型和位置信息
- **多表格区域**：自动检测单个 Sheet 内的多个表格（通过空行分隔），支持切换查看

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | MySQL 8.0 |
| 部署 | Docker + Docker Compose |

## 项目结构

```
├── backend/                # 后端服务
│   ├── app/
│   │   ├── main.py        # FastAPI 入口
│   │   ├── config.py      # 配置文件
│   │   ├── database.py    # 数据库连接
│   │   ├── models.py      # 数据模型
│   │   ├── schemas.py     # Pydantic 模型
│   │   ├── crud.py        # 数据库操作
│   │   └── routers/
│   │       └── excel.py   # API 路由
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # 前端服务
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── api/
│   │   └── components/
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 数据库模型

系统使用以下数据表存储 Excel 数据：

| 表名 | 说明 |
|------|------|
| excel_files | Excel 文件信息（包含原始文件二进制数据） |
| excel_sheets | Sheet 信息 |
| excel_data | 单元格数据 |
| merged_cells | 合并单元格信息 |
| sheet_images | 内嵌图片数据 |
| sheet_charts | 内嵌图表信息 |
| table_regions | 表格区域信息（多表头支持） |

## 快速开始

### 使用 Docker（推荐）

```bash
# 克隆项目后进入目录
cd Execl

# 启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps
```

启动完成后访问：
- 前端界面：http://localhost
- API 文档：http://localhost:8000/docs

### 停止服务

```bash
docker-compose down
```

### 重建数据库

如果从旧版本升级，需要重建数据库以创建新表：

```bash
# 停止服务并删除数据卷
docker-compose down -v

# 重新启动
docker-compose up -d --build
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload | 上传 Excel 文件 |
| GET | /api/files | 获取文件列表 |
| GET | /api/files/{id} | 获取文件详情 |
| GET | /api/files/{id}/sheets/{sheet_id}/data | 获取 Sheet 数据（含合并单元格、图片、图表、表格区域） |
| GET | /api/files/{id}/download | 下载文件 |
| GET | /api/images/{image_id} | 获取图片二进制数据 |
| DELETE | /api/files/{id} | 删除文件 |

### Sheet 数据响应结构

```json
{
  "sheet_id": 1,
  "sheet_name": "Sheet1",
  "total_rows": 100,
  "total_columns": 10,
  "page": 1,
  "page_size": 50,
  "headers": ["列1", "列2", ...],
  "data": [["值1", "值2", ...], ...],
  "merged_cells": [
    {"start_row": 0, "start_col": 0, "end_row": 1, "end_col": 2}
  ],
  "images": [
    {"id": 1, "image_format": "png", "anchor_row": 5, "anchor_col": 3, "width": 200, "height": 150}
  ],
  "charts": [
    {"id": 1, "chart_type": "bar", "chart_title": "销售图表", "anchor_row": 10, "anchor_col": 0}
  ],
  "table_regions": [
    {"id": 1, "region_index": 0, "start_row": 0, "end_row": 20, "table_name": "表格1"},
    {"id": 2, "region_index": 1, "start_row": 25, "end_row": 50, "table_name": "表格2"}
  ]
}
```

## 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATABASE_URL | mysql+pymysql://root:password@localhost:3306/excel_manager | 数据库连接字符串 |

### 文件限制

- 最大文件大小：50MB
- 支持格式：.xls, .xlsx

## 功能说明

### 合并单元格

- 上传时自动解析 Excel 中的合并单元格信息
- 前端使用原生 HTML table 的 colspan/rowspan 正确渲染合并效果
- 合并单元格会以浅黄色背景高亮显示

### 内嵌图片

- 支持 .xlsx 格式中的内嵌图片提取
- 图片存储在数据库中，通过 API 获取
- 前端显示图片缩略图，点击可预览大图
- 显示图片在 Excel 中的锚定位置（如 A1、B5）

### 内嵌图表

- 识别常见图表类型：柱状图、折线图、饼图、面积图、散点图等
- 显示图表标题和锚定位置
- 注：目前仅显示图表元信息，不进行可视化渲染

### 多表格区域

- 自动检测单个 Sheet 内通过空行分隔的多个表格
- 工具栏显示表格区域选择器
- 可选择查看全部数据或单个表格区域
- 表格名称自动取第一行第一个非空单元格的值

## 注意事项

- `.xls` 格式的图片和图表提取暂不支持（xlrd 库限制）
- 图表目前只展示元信息，没有可视化渲染
- 大文件建议使用分页模式查看

## 许可证

MIT License
