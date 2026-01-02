# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个基于 Web 的 Excel 文件管理系统，支持多用户认证、数据隔离，以及高级 Excel 解析功能（合并单元格、内嵌图片、图表、多表格区域）。项目采用前后端分离架构，使用 Docker Compose 进行部署。

## 语言

用中文输出和交互

## 常用命令

### Docker 开发（推荐）
```bash
# 启动所有服务
docker compose up -d --build

# 运行数据库迁移
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务（保留数据）
docker compose down

# 停止服务并删除数据卷
docker compose down -v
```

### 前端开发
```bash
cd frontend
npm install          # 安装依赖
npm run dev          # 启动开发服务器（Vite）
npm run build        # 生产构建
npm run preview      # 预览生产构建
```

### 后端开发
```bash
cd backend
pip install -r requirements.txt    # 安装依赖
# 先设置 DATABASE_URL 环境变量
# 然后运行: uvicorn app.main:app --reload
```

### 数据库迁移
初次部署 Docker 后，运行迁移脚本添加认证相关表：
```bash
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

这将创建一个默认用户（用户名：`migrated_user`，密码：`default123`）用于迁移现有数据。

## 架构

### 后端（Python/FastAPI）
- **入口文件**：`backend/app/main.py` - FastAPI 应用，配置 CORS 和 Session 中间件
- **配置文件**：`backend/app/config.py` - 基于环境变量的配置（数据库、文件限制、会话设置）
- **数据模型**：`backend/app/models.py` - SQLAlchemy ORM 模型（User、Session、ExcelFile、ExcelSheet、ExcelData、MergedCell、SheetImage、SheetChart、TableRegion）
- **CRUD 操作**：`backend/app/crud.py` - 数据库访问层，包含批量操作以提升性能
- **认证模块**：`backend/app/auth.py` - 基于 Session 的认证，使用 bcrypt 哈希密码，`get_current_user` 依赖用于保护路由
- **路由**：
  - `backend/app/routers/auth.py` - 注册、登录、登出、用户信息接口
  - `backend/app/routers/excel.py` - 文件上传、列表、详情、下载、删除和数据查询

### 前端（Vue 3 + Vite + Element Plus + Pinia）
- **入口文件**：`frontend/src/main.js`
- **状态管理**：`frontend/src/stores/auth.js` - Pinia 认证状态存储
- **API 层**：
  - `frontend/src/api/auth.js` - 认证 API 调用
  - `frontend/src/api/excel.js` - Excel API，包含 axios 实例、请求/响应拦截器处理认证令牌
- **组件**：登录、注册、文件上传、文件列表、数据表格（全屏表格查看器）

### 认证流程
1. 用户注册/登录 → 服务端创建 Session 记录 → 返回令牌
2. 客户端将令牌存储在 localStorage（`session_token`）
3. Axios 请求拦截器添加 `Authorization: Bearer {token}` 请求头
4. 服务端通过 `get_current_user` 依赖验证会话
5. 响应拦截器处理 401/403 错误（清除令牌、重定向到登录页）
6. 所有文件操作通过 `user_id` 过滤强制用户隔离

### Excel 解析架构
- **上传处理器**（`excel.py:324-417`）：接收文件 → 验证 → 根据扩展名解析 → 保存二进制文件 + 结构化数据
- **解析函数**：
  - `parse_xlsx()`：使用 openpyxl，提取合并单元格、图片、图表，检测多表格区域
  - `parse_xls()`：使用 xlrd，支持合并单元格和表格区域（不支持图片/图表）
- **表格区域检测**（`excel.py:28-98`）：通过检测空行作为分隔符，识别单个 Sheet 中的多个表格
- **数据存储**：二进制文件存储在 `excel_files.file_data`，解析后的数据存储在关联表中

### 数据隔离
- 每个 `ExcelFile` 都有 `user_id` 外键
- 所有 CRUD 操作都通过 `user_id` 过滤（见 `crud.py:165-188`）
- 图片下载接口在提供服务前验证文件归属
- 配置级联删除：删除文件会移除所有关联的 sheets、数据、图片、图表

## 关键技术细节

### 会话管理
- 会话存储在 `sessions` 表中，包含 `expires_at` 时间戳
- 会话 ID 使用 `secrets.token_urlsafe(32)` 生成
- 会话过期由 `SESSION_EXPIRE_HOURS` 配置控制（默认 24 小时）
- 客户端将令牌存储在 localStorage，服务端在每次请求时验证会话

### 文件上传限制
- 最大文件大小：50MB（config.py 中的 `MAX_FILE_SIZE`）
- 允许的扩展名：`.xls`、`.xlsx`
- 文件以二进制形式存储在数据库中（`LargeBinary` 列）

### 分页
- Sheet 数据 API 支持分页：`page` 和 `page_size` 参数（最大 50000）
- 文件列表 API 支持 `skip` 和 `limit` 参数（最大 100）

### 环境变量
- `DATABASE_URL`：MySQL 连接字符串
- `SESSION_SECRET`：会话加密密钥（生产环境请修改）
- `SESSION_EXPIRE_HOURS`：会话有效期（小时）

### 服务端口
- 前端：http://localhost（端口 80）
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- MySQL：localhost:3306
