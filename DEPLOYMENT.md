# 🎉 部署手册

本文档介绍 Excel 文件管理系统的部署方式。系统采用青春活力设计风格，支持多用户、用户认证、上传、存储、查看、下载和删除 Excel 文件。

## 📋 目录

- [🌍 环境要求](#环境要求)
- [🐳 Docker 部署（推荐）](#docker-部署推荐)
- [📦 侧载部署](#侧载部署)
- [💻 本地开发部署](#本地开发部署)
- [💾 数据库说明](#数据库说明)
- [⚙️ 生产环境配置](#生产环境配置)
- [❓ 常见问题](#常见问题)
- [🔧 服务管理命令](#服务管理命令)
- [✨ 功能说明](#功能说明)

---

<div align="center">
  <img src="https://img.shields.io/badge/Excel-管理专家-brightgreen?style=for-the-badge&logo=microsoft-excel" alt="Excel 管理专家">
  <p>🎨 青春活力主题 | 🚀 高性能部署 | 🔒 安全可靠</p>
</div>

---

## 🌍 环境要求

### 🐳 Docker 部署

- Docker 20.10+
- Docker Compose 2.0+
- 可用端口：80（前端）、8000（后端）、3306（MySQL）

### 💻 本地开发

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

---

## 🐳 Docker 部署（推荐）

### 📌 1. 准备工作

确保已安装 Docker 和 Docker Compose：

```bash
docker --version
docker compose version
```

### 🚀 2. 启动服务

```bash
cd Execl
docker compose up -d --build
```

🎉 首次启动需要构建镜像，请耐心等待几分钟。

### 📊 3. 执行数据库迁移

启动服务后，需要执行数据库迁移脚本以添加用户认证相关的表：

```bash
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

✨ 迁移脚本会：
- 🔐 创建 users 表（用户信息）
- 🎫 创建 sessions 表（用户会话）
- 🔗 修改 excel_files 表添加 user_id 外键
- 👤 创建默认迁移用户（用户名：migrated_user，密码：default123）
- 📁 将现有文件关联到默认用户

### ✅ 4. 验证部署

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

所有服务状态应为 `running`：

```
NAME              STATUS
excel-mysql      running (healthy)
excel-backend    running
excel-frontend   running
```

### 🌐 5. 访问应用

| 服务 | 地址 | 描述 |
|------|------|------|
| 🎨 前端界面 | http://localhost | 青春活力风格界面 |
| 📚 API 文档 | http://localhost:8000/docs | 后端 API 接口文档 |
| 💾 MySQL | localhost:3306 | 数据库服务 |

### 👤 6. 首次登录

1. 🌐 访问 http://localhost
2. 🔐 使用默认用户登录或注册新用户：
   - 📝 默认用户名：`migrated_user`
   - 🔑 默认密码：`default123`
3. 🎯 登录后建议修改默认用户密码或注册新用户

### 🛑 7. 停止服务

```bash
# 停止服务（保留数据）
docker compose down

# 停止服务并删除数据卷
docker compose down -v
```

---

## 📦 侧载部署

侧载部署适用于需要将 Docker 镜像导出后在离线环境部署的场景。

### 🏗️ 1. 构建并导出镜像

在有网络的机器上执行：

```bash
cd Execl

# 构建镜像
docker compose build

# 导出镜像
docker save execl-backend:latest -o execl-backend.tar
docker save execl-frontend:latest -o execl-frontend.tar
docker save mysql:8.0 -o mysql.tar
```

### 📤 2. 传输文件

将以下文件传输到目标机器：

- `execl-backend.tar`
- `execl-frontend.tar`
- `mysql.tar`
- `docker-compose.yml`
- `backend/migration.sql`

### 📥 3. 导入镜像

在目标机器上执行：

```bash
docker load -i mysql.tar
docker load -i execl-backend.tar
docker load -i execl-frontend.tar
```

### ✏️ 4. 修改 docker-compose.yml

将构建指令改为使用镜像：

```yaml
services:
  mysql:
    image: mysql:8.0
    # ... 其他配置不变

  backend:
    image: execl-backend:latest  # 改为 image
    # build: ./backend          # 注释掉 build
    # ... 其他配置不变

  frontend:
    image: execl-frontend:latest  # 改为 image
    # build: ./frontend          # 注释掉 build
    # ... 其他配置不变
```

### 🚀 5. 启动服务并执行迁移

```bash
docker compose up -d
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

---

## 💻 本地开发部署

### 💾 1. 启动 MySQL

可以使用 Docker 快速启动 MySQL：

```bash
docker run -d \
  --name excel-mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=excel_manager \
  -p 3306:3306 \
  mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

或使用本地安装的 MySQL，创建数据库：

```sql
CREATE DATABASE excel_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 📊 2. 执行数据库迁移

```bash
mysql -uroot -ppassword excel_manager < backend/migration.sql
```

### ⚡ 3. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（可选，使用默认值则跳过）
# Windows:
set DATABASE_URL=mysql+pymysql://root:password@localhost:3306/excel_manager
# Linux/Mac:
export DATABASE_URL=mysql+pymysql://root:password@localhost:3306/excel_manager

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

📚 后端启动后访问 http://localhost:8000/docs 查看 API 文档。

### 🎨 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

🌐 前端启动后访问 http://localhost:3000

---

## 💾 数据库说明

### 📊 数据表结构

系统使用以下数据表存储数据：

| 表名 | 说明 |
|------|------|
| 👤 users | 用户信息（用户名、邮箱、密码哈希） |
| 🎫 sessions | 用户会话（session_id、过期时间） |
| 📁 excel_files | Excel 文件信息（包含原始文件二进制数据、user_id） |
| 📄 excel_sheets | Sheet 信息 |
| 📝 excel_data | 单元格数据 |
| 🔗 merged_cells | 合并单元格信息 |
| 🖼️ sheet_images | 内嵌图片数据（MEDIUMBLOB，最大 16MB） |
| 📈 sheet_charts | 内嵌图表信息（JSON 格式存储） |
| 🗂️ table_regions | 表格区域信息（多表头支持） |

### 🔄 数据库迁移

从 v2.0 升级到 v3.0 需要执行数据库迁移：

```bash
# 执行迁移脚本
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

**⚠️ 注意**：
- 🔐 迁移脚本会创建默认用户 `migrated_user`（密码：`default123`）
- 📁 现有文件会关联到该默认用户
- 🎯 建议迁移后注册新用户并删除默认用户

### 数据库表结构

#### 用户表

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

#### 会话表

```sql
CREATE TABLE sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);
```

#### 合并单元格表

```sql
CREATE TABLE merged_cells (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sheet_id INT NOT NULL,
    start_row INT NOT NULL,
    start_col INT NOT NULL,
    end_row INT NOT NULL,
    end_col INT NOT NULL,
    FOREIGN KEY (sheet_id) REFERENCES excel_sheets(id) ON DELETE CASCADE
);
```

#### 图片表

```sql
CREATE TABLE sheet_images (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sheet_id INT NOT NULL,
    image_data MEDIUMBLOB NOT NULL,
    image_format VARCHAR(20) NOT NULL,
    anchor_type VARCHAR(20) DEFAULT 'oneCellAnchor',
    anchor_row INT NOT NULL,
    anchor_col INT NOT NULL,
    width INT,
    height INT,
    FOREIGN KEY (sheet_id) REFERENCES excel_sheets(id) ON DELETE CASCADE
);
```

#### 图表表

```sql
CREATE TABLE sheet_charts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sheet_id INT NOT NULL,
    chart_type VARCHAR(50) NOT NULL,
    chart_title VARCHAR(255),
    chart_data JSON,
    anchor_row INT NOT NULL,
    anchor_col INT NOT NULL,
    width INT,
    height INT,
    FOREIGN KEY (sheet_id) REFERENCES excel_sheets(id) ON DELETE CASCADE
);
```

#### 表格区域表

```sql
CREATE TABLE table_regions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sheet_id INT NOT NULL,
    region_index INT NOT NULL,
    start_row INT NOT NULL,
    start_col INT NOT NULL,
    end_row INT NOT NULL,
    end_col INT NOT NULL,
    header_rows INT DEFAULT 1,
    table_name VARCHAR(255),
    FOREIGN KEY (sheet_id) REFERENCES excel_sheets(id) ON DELETE CASCADE
);
```

---

## ⚙️ 生产环境配置

### 🔐 修改数据库密码

编辑 `docker-compose.yml`：

```yaml
mysql:
  environment:
    MYSQL_ROOT_PASSWORD: your_secure_password  # 修改此处

backend:
  environment:
    DATABASE_URL: mysql+pymysql://root:your_secure_password@mysql:3306/excel_manager
```

### 🎫 修改 Session 密钥

```yaml
backend:
  environment:
    SESSION_SECRET: your-random-secret-key-min-32-chars  # 生成强随机密钥
```

生成强随机密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 🌐 修改端口

```yaml
frontend:
  ports:
    - "8080:80"  # 将 80 改为其他端口

backend:
  ports:
    - "9000:8000"  # 将 8000 改为其他端口
```

如果修改了后端端口，需要同步修改 `frontend/nginx.conf`：

```nginx
location /api {
    proxy_pass http://backend:8000;  # 容器内端口不变
}
```

### 💾 数据持久化

MySQL 数据默认存储在 Docker 卷中。查看数据卷：

```bash
docker volume ls
```

备份数据：

```bash
docker exec excel-mysql mysqldump -uroot -ppassword excel_manager > backup.sql
```

恢复数据：

```bash
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backup.sql
```

---

## ❓ 常见问题

### 🔌 1. 端口被占用

```
Error: bind: address already in use
```

**解决方案**：
- 🔄 修改 `docker-compose.yml` 中的端口映射
- 🛑 或停止占用端口的服务

### 🗄️ 2. MySQL 连接失败

```
Can't connect to MySQL server
```

**解决方案**：
- ⏱️ 等待 MySQL 完全启动（查看 `docker compose logs mysql`）
- 🔍 检查 DATABASE_URL 配置是否正确

### 🌐 3. 前端无法访问后端 API

检查 `frontend/nginx.conf` 中的代理配置：

```nginx
location /api {
    proxy_pass http://backend:8000;
}
```

### 📤 4. 文件上传失败

- 📏 检查文件大小是否超过 50MB
- 📄 检查文件格式是否为 .xls 或 .xlsx
- 📋 查看后端日志：`docker compose logs backend`
- 🔐 确认已登录

### 🔐 5. 登录失败

- ✅ 确认已执行数据库迁移脚本
- 🔑 检查用户名和密码是否正确
- 📋 查看后端日志：`docker compose logs backend`

### ⏰ 6. Session 过期

- 🕐 Session 默认有效期为 24 小时
- 🔄 过期后需要重新登录
- 🎛️ 可通过 SESSION_EXPIRE_HOURS 环境变量调整

### 🔄 7. 合并单元格显示不正确

- 🚀 确保使用最新版本的前端代码
- 🧹 清除浏览器缓存后刷新页面
- 📋 检查后端日志确认解析是否成功

### 🖼️ 8. 图片无法显示

- ✅ 确认上传的是 .xlsx 格式文件（.xls 格式暂不支持图片提取）
- 📋 检查后端日志是否有图片解析错误
- 🔐 确认用户有权限访问该图片
- 🧪 通过 API 测试图片接口：`GET /api/images/{image_id}`

### 📥 9. 下载文件失败

- 📋 检查后端日志是否有错误
- 🌐 中文文件名使用 RFC 5987 编码格式
- 🔐 确认用户有权限访问该文件

### 📊 10. 分页切换到全部模式失败

- ✅ 确保后端 `page_size` 参数限制已更新为 50000
- 🔄 重新构建后端镜像：`docker compose build --no-cache backend`

### 🗑️ 11. 重置所有数据

```bash
docker compose down -v
docker compose up -d --build
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

---

## 🔧 服务管理命令

### 📊 服务状态
```bash
# 查看所有服务状态
docker compose ps

# 查看实时日志
docker compose logs -f [service_name]

# 重启服务
docker compose restart [service_name]

# 重建并启动单个服务
docker compose up -d --build backend
docker compose up -d --build frontend

# 重建所有服务（不使用缓存）
docker compose build --no-cache
docker compose up -d
```

### 🛠️ 容器操作
```bash
# 进入容器
docker exec -it excel-backend /bin/bash
docker exec -it excel-frontend /bin/bash
docker exec -it excel-mysql mysql -uroot -ppassword

# 清理未使用的镜像
docker image prune

# 查看容器资源使用情况
docker stats
```

### 💾 数据管理
```bash
# 备份数据库
docker exec excel-mysql mysqldump -uroot -ppassword excel_manager > backup.sql

# 恢复数据库
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backup.sql

# 执行数据库迁移
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql

# 查看数据库大小
docker exec excel-mysql mysql -uroot -ppassword -e "SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size in MB' FROM information_schema.tables WHERE table_schema='excel_manager';"
```

---

## ✨ 功能说明

### 🔐 认证功能

| 功能 | 说明 |
|------|------|
| 👤 用户注册 | 用户名（3-50字符）、邮箱验证、密码最少6位 |
| 🔐 用户登录 | Session + Cookie 认证，有效期24小时 |
| 👋 用户登出 | 清除服务端 Session 和客户端状态 |
| 🔒 数据隔离 | 用户只能访问自己的文件和数据 |

### 🚀 支持的 Excel 特性

| 特性 | .xlsx | .xls |
|------|-------|------|
| 📊 单元格数据 | ✅ | ✅ |
| 🔄 合并单元格 | ✅ | ✅ |
| 🖼️ 内嵌图片 | ✅ | ❌ |
| 📈 内嵌图表 | ✅ (元信息) | ❌ |
| 📋 多表格区域 | ✅ | ✅ |
| 🌐 中文文件名下载 | ✅ | ✅ |
| 🔐 用户数据隔离 | ✅ | ✅ |

### 🎨 界面说明

#### 🔐 登录/注册页
- 📝 登录表单（用户名、密码）
- 📝 注册表单（用户名、邮箱、密码、确认密码）
- ✅ 表单验证和错误提示
- 🔗 登录/注册切换链接

#### 📁 文件列表页
- 👤 显示当前用户名
- 🚪 退出登录按钮
- 📤 拖拽上传区域
- 📄 文件列表（文件名、大小、Sheet 数、上传时间）
- 👆 点击行进入数据查看页
- 💾 下载和删除按钮

#### 📊 数据查看页（全屏）
- **🔧 工具栏**：返回按钮、文件名、Sheet 选择器、表格区域选择器、分页开关、每页行数、下载按钮
- **🖼️ 图片/图表区**（可折叠）：显示内嵌图片缩略图和图表信息
- **📋 数据表格**：
  - 🔢 行号列固定在左侧
  - 📑 表头固定在顶部
  - 🎭 斑马纹（奇偶行交替颜色）
  - ✨ 悬停高亮
  - 🔄 合并单元格（浅黄色背景）
  - 📊 Excel 风格列号（A, B, C, ..., AA, AB）
- **📊 状态栏**：行数 × 列数、当前 Sheet、合并单元格数、表格区域数、分页器

### 🗂️ 多表格区域检测

系统通过识别 Sheet 中的空行来自动分割多个表格区域。当一个 Sheet 中存在多个通过空行分隔的数据块时，会自动识别为多个表格区域，用户可以在前端切换查看。

### 📦 依赖包说明

#### ⚙️ 后端依赖（requirements.txt）
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `sqlalchemy` - ORM
- `pymysql` - MySQL 驱动
- `cryptography` - MySQL 8.0 认证支持
- `passlib[bcrypt]` - bcrypt 密码哈希
- `openpyxl` - .xlsx 文件解析
- `xlrd` - .xls 文件解析
- `python-multipart` - 文件上传支持

#### 🎨 前端依赖（package.json）
- `vue` - Vue 3 框架
- `vite` - 构建工具
- `element-plus` - UI 组件库
- `pinia` - 状态管理
- `axios` - HTTP 客户端
