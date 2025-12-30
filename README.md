# Excel 文件管理系统

一个基于 Web 的 Excel 文件管理系统，支持上传、存储、查看、下载和删除 Excel 文件。

## 功能特性

- **文件上传**：支持 .xls 和 .xlsx 格式，拖拽或点击上传
- **文件存储**：原始文件二进制存储 + 解析数据结构化存储
- **数据展示**：表格形式展示，支持分页和多 Sheet 切换
- **文件下载**：下载原始 Excel 文件
- **文件删除**：删除文件及关联数据

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

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload | 上传 Excel 文件 |
| GET | /api/files | 获取文件列表 |
| GET | /api/files/{id} | 获取文件详情 |
| GET | /api/files/{id}/sheets/{sheet_id}/data | 获取 Sheet 数据 |
| GET | /api/files/{id}/download | 下载文件 |
| DELETE | /api/files/{id} | 删除文件 |

## 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATABASE_URL | mysql+pymysql://root:password@localhost:3306/excel_manager | 数据库连接字符串 |

### 文件限制

- 最大文件大小：50MB
- 支持格式：.xls, .xlsx

## 许可证

MIT License
