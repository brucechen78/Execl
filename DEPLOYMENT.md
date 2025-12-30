# 部署手册

本文档介绍 Excel 文件管理系统的部署方式。

## 目录

- [环境要求](#环境要求)
- [Docker 部署（推荐）](#docker-部署推荐)
- [侧载部署](#侧载部署)
- [本地开发部署](#本地开发部署)
- [常见问题](#常见问题)

---

## 环境要求

### Docker 部署

- Docker 20.10+
- Docker Compose 2.0+
- 可用端口：80（前端）、8000（后端）、3306（MySQL）

### 本地开发

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

---

## Docker 部署（推荐）

### 1. 准备工作

确保已安装 Docker 和 Docker Compose：

```bash
docker --version
docker-compose --version
```

### 2. 启动服务

```bash
cd Execl
docker-compose up -d --build
```

首次启动需要构建镜像，可能需要几分钟。

### 3. 验证部署

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

### 4. 访问应用

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost |
| API 文档 | http://localhost:8000/docs |
| MySQL | localhost:3306 |

### 5. 停止服务

```bash
# 停止服务（保留数据）
docker-compose down

# 停止服务并删除数据卷
docker-compose down -v
```

---

## 侧载部署

侧载部署适用于需要将 Docker 镜像导出后在离线环境部署的场景。

### 1. 构建并导出镜像

在有网络的机器上执行：

```bash
cd Execl

# 构建镜像
docker-compose build

# 导出镜像
docker save execl-backend:latest -o execl-backend.tar
docker save execl-frontend:latest -o execl-frontend.tar
docker save mysql:8.0 -o mysql.tar
```

### 2. 传输文件

将以下文件传输到目标机器：

- `execl-backend.tar`
- `execl-frontend.tar`
- `mysql.tar`
- `docker-compose.yml`

### 3. 导入镜像

在目标机器上执行：

```bash
docker load -i mysql.tar
docker load -i execl-backend.tar
docker load -i execl-frontend.tar
```

### 4. 修改 docker-compose.yml

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

### 5. 启动服务

```bash
docker-compose up -d
```

---

## 本地开发部署

### 1. 启动 MySQL

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

### 2. 启动后端

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

后端启动后访问 http://localhost:8000/docs 查看 API 文档。

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后访问 http://localhost:3000

---

## 生产环境配置

### 修改数据库密码

编辑 `docker-compose.yml`：

```yaml
mysql:
  environment:
    MYSQL_ROOT_PASSWORD: your_secure_password  # 修改此处

backend:
  environment:
    DATABASE_URL: mysql+pymysql://root:your_secure_password@mysql:3306/excel_manager
```

### 修改端口

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

### 数据持久化

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

## 常见问题

### 1. 端口被占用

```
Error: bind: address already in use
```

解决方案：
- 修改 `docker-compose.yml` 中的端口映射
- 或停止占用端口的服务

### 2. MySQL 连接失败

```
Can't connect to MySQL server
```

解决方案：
- 等待 MySQL 完全启动（查看 `docker-compose logs mysql`）
- 检查 DATABASE_URL 配置是否正确

### 3. 前端无法访问后端 API

检查 `frontend/nginx.conf` 中的代理配置：

```nginx
location /api {
    proxy_pass http://backend:8000;
}
```

### 4. 文件上传失败

- 检查文件大小是否超过 50MB
- 检查文件格式是否为 .xls 或 .xlsx
- 查看后端日志：`docker-compose logs backend`

### 5. 重置所有数据

```bash
docker-compose down -v
docker-compose up -d --build
```

---

## 服务管理命令

```bash
# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 重建并启动
docker-compose up -d --build

# 进入容器
docker exec -it excel-backend /bin/bash
docker exec -it excel-mysql mysql -uroot -ppassword

# 清理未使用的镜像
docker image prune
```
