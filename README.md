# Excel 文件管理系统

一个基于 Web 的 Excel 文件管理系统，支持多用户、用户认证、上传、存储、查看、下载和删除 Excel 文件，用户间数据完全隔离。

## 功能特性

### 认证功能
- **用户注册**：用户名、邮箱注册，密码最少 6 位
- **用户登录**：Session + Cookie 认证，有效期 24 小时
- **用户登出**：清除服务端和客户端状态
- **数据隔离**：用户只能访问自己的文件和数据

### 核心功能
- **文件上传**：支持 .xls 和 .xlsx 格式，拖拽或点击上传，文件关联当前用户
- **文件存储**：原始文件二进制存储 + 解析数据结构化存储，用户级数据隔离
- **数据展示**：全屏表格展示，支持分页/全部显示切换、多 Sheet 切换，仅显示当前用户文件
- **文件管理**：文件列表展示（仅当前用户）、文件下载、文件删除

### 高级功能
- **合并单元格**：正确解析和渲染 Excel 中的合并单元格（浅黄色高亮）
- **内嵌图片**：提取并展示 Excel 中的图片，支持点击预览大图
- **内嵌图表**：识别图表类型和位置信息
- **多表格区域**：自动检测单个 Sheet 内的多个表格（通过空行分隔），支持切换查看

## 界面预览

### 登录/注册页
- 用户登录和注册表单
- 表单验证和错误提示
- 登录/注册状态切换

### 文件列表页
- 显示当前用户名和退出登录按钮
- 拖拽上传区域
- 文件列表（文件名、大小、Sheet 数、上传时间）
- 支持下载和删除操作

### 数据查看页（全屏）
- 顶部工具栏：返回按钮、文件名、Sheet 选择器、表格区域选择器、分页开关、下载按钮
- 图片/图表展示区（可折叠）
- 全屏数据表格：行号固定、表头固定、斑马纹、悬停高亮
- 底部状态栏：行列数、当前 Sheet、合并单元格数、表格区域数、分页器

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 后端 | Python + FastAPI + SQLAlchemy + Passlib |
| 数据库 | MySQL 8.0 |
| 部署 | Docker + Docker Compose |
| 认证 | Session + Cookie + bcrypt |

## 项目结构

```
├── backend/                # 后端服务
│   ├── app/
│   │   ├── main.py        # FastAPI 入口
│   │   ├── config.py      # 配置文件
│   │   ├── database.py    # 数据库连接
│   │   ├── models.py      # 数据模型（User, Session, Excel）
│   │   ├── schemas.py     # Pydantic 模型
│   │   ├── crud.py        # 数据库操作
│   │   ├── auth.py        # 认证工具函数
│   │   └── routers/
│   │       ├── auth.py    # 认证 API 路由
│   │       └── excel.py   # Excel API 路由
│   ├── requirements.txt
│   ├── migration.sql      # 数据库迁移脚本
│   └── Dockerfile
├── frontend/              # 前端服务
│   ├── src/
│   │   ├── App.vue        # 主应用（包含认证流程）
│   │   ├── main.js
│   │   ├── stores/
│   │   │   └── auth.js    # 认证状态管理（Pinia）
│   │   ├── api/
│   │   │   ├── auth.js    # 认证 API
│   │   │   └── excel.js   # Excel API（含认证拦截器）
│   │   └── components/
│   │       ├── Login.vue      # 登录组件
│   │       ├── Register.vue   # 注册组件
│   │       ├── FileUpload.vue # 上传组件
│   │       ├── FileList.vue   # 文件列表
│   │       └── DataTable.vue  # 数据表格（全屏）
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── README.md
└── DEPLOYMENT.md          # 详细部署手册
```

## 数据库模型

系统使用以下数据表存储数据：

| 表名 | 说明 |
|------|------|
| users | 用户信息（用户名、邮箱、密码哈希） |
| sessions | 用户会话（session_id、过期时间） |
| excel_files | Excel 文件信息（包含原始文件二进制数据、user_id） |
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

# 执行数据库迁移（添加用户认证相关表）
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

首次启动需要构建镜像，可能需要几分钟。

### 验证部署

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

所有服务状态应为 `running`：

```
NAME              STATUS
excel-mysql      running (healthy)
excel-backend    running
excel-frontend   running
```

### 访问应用

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost |
| API 文档 | http://localhost:8000/docs |
| MySQL | localhost:3306 |

### 首次登录

数据库迁移后会创建一个默认用户用于迁移现有数据：

- 用户名：`migrated_user`
- 密码：`default123`

登录后建议：
1. 注册新用户
2. 删除默认用户或修改其密码

### 停止服务

```bash
# 停止服务（保留数据）
docker-compose down

# 停止服务并删除数据卷
docker-compose down -v
```

## API 接口

### 认证 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/logout | 用户登出 |
| GET | /api/auth/me | 获取当前用户信息 |

### 文件 API（需要认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload | 上传 Excel 文件 |
| GET | /api/files | 获取当前用户的文件列表 |
| GET | /api/files/{id} | 获取文件详情 |
| GET | /api/files/{id}/sheets/{sheet_id}/data | 获取 Sheet 数据（含合并单元格、图片、图表、表格区域） |
| GET | /api/files/{id}/download | 下载文件（支持中文文件名） |
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
  "headers": ["列1", "列2", "..."],
  "data": [["值1", "值2", "..."], "..."],
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
| SESSION_SECRET | excel-manager-secret-key-change-in-production-2024 | Session 加密密钥 |
| SESSION_EXPIRE_HOURS | 24 | Session 有效期（小时） |

### 文件限制

- 最大文件大小：50MB
- 支持格式：.xls, .xlsx
- 分页模式：20/50/100/200/500 条/页
- 全部模式：最多 50000 行

## 功能说明

### 认证流程

1. **注册**：用户填写用户名、邮箱、密码，注册成功后自动登录
2. **登录**：使用用户名/密码登录，服务端创建 Session，返回 token
3. **认证**：所有 API 请求携带 token，服务端验证用户身份
4. **登出**：清除服务端 Session 和客户端状态

### 数据隔离

- 每个用户只能访问自己上传的文件
- 文件上传时自动关联当前用户 ID
- 所有 API 请求都验证用户权限
- 图片下载也验证文件归属

### 表格展示

- **全屏显示**：点击文件后进入全屏数据查看页面
- **斑马纹**：奇偶行交替颜色（白色/浅灰）
- **悬停高亮**：鼠标悬停行变为浅蓝色
- **列号显示**：每列显示 Excel 风格列号（A, B, C, ..., AA, AB）
- **行号固定**：行号列固定在左侧
- **表头固定**：表头固定在顶部

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
- 中文文件名下载使用 RFC 5987 编码格式
- 所有 API 请求都需要用户认证
- Session 过期后需重新登录

## 安全说明

- 密码使用 bcrypt 加密存储
- Session ID 使用加密随机字符串生成
- 用户间数据完全隔离
- 建议在生产环境修改 SESSION_SECRET

## 许可证

MIT License
