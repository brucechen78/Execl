# 🎉 Deployment Guide

This document describes the deployment methods for the Excel File Management System with **youthful design** theme.

![Excel Expert](https://img.shields.io/badge/Excel-Management-Expert-brightgreen?style=for-the-badge&logo=microsoft-excel)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql)

## 📋 Table of Contents

- [🌍 System Requirements](#system-requirements)
- [🐳 Docker Deployment (Recommended)](#docker-deployment-recommended)
- [📦 Sideload Deployment](#sideload-deployment)
- [💻 Local Development Deployment](#local-development-deployment)
- [💾 Database Information](#database-information)
- [⚙️ Production Configuration](#production-configuration)
- [❓ Troubleshooting](#troubleshooting)
- [🔧 Service Management Commands](#service-management-commands)
- [✨ Feature Documentation](#feature-documentation)

---

<div align="center">
  <img src="https://img.shields.io/badge/Excel-Management-Expert-brightgreen?style=for-the-badge&logo=microsoft-excel" alt="Excel Management Expert">
  <p>🎨 Youthful Theme | 🚀 High Performance Deployment | 🔒 Secure & Reliable</p>
</div>

---

## 🌍 System Requirements

### 🐳 Docker Deployment

- Docker 20.10+
- Docker Compose 2.0+
- Available ports: 80 (frontend), 8000 (backend), 3306 (MySQL)

### 💻 Local Development

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

---

## 🐳 Docker Deployment (Recommended)

### 📌 1. Preparation

Ensure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

### 🚀 2. Start Services

```bash
cd Execl
docker-compose up -d --build
```

🎉 First startup requires image building and may take a few minutes.

### 📊 3. Execute Database Migration

After starting services, execute the database migration script to add user authentication tables:

```bash
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

✨ Migration script will:
- 🔐 Create users table (user information)
- 🎫 Create sessions table (user sessions)
- 🔗 Modify excel_files table to add user_id foreign key
- 👤 Create default migration user (username: migrated_user, password: default123)
- 📁 Associate existing files with the default user

### ✅ 4. Verify Deployment

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

All services should show status `running`:

```
NAME              STATUS
excel-mysql      running (healthy)
excel-backend    running
excel-frontend   running
```

### 🌐 5. Access Application

| Service | Address | Description |
|---------|---------|-------------|
| 🎨 Frontend | http://localhost | Youthful style interface |
| 📚 API Documentation | http://localhost:8000/docs | Backend API documentation |
| 💾 MySQL | localhost:3306 | Database service |

### 👤 6. First Login

1. Visit http://localhost
2. Login with default user or register a new user:
   - Default username: `migrated_user`
   - Default password: `default123`
3. After login, it's recommended to register a new user and delete the default user

### 🛑 7. Stop Services

```bash
# Stop services (keep data)
docker-compose down

# Stop services and remove data volumes
docker-compose down -v
```

---

## 📦 Sideload Deployment

Sideload deployment is useful for scenarios requiring offline deployment by exporting Docker images.

### 🏗️ 1. Build and Export Images

On a machine with network access:

```bash
cd Execl

# Build images
docker-compose build

# Export images
docker save execl-backend:latest -o execl-backend.tar
docker save execl-frontend:latest -o execl-frontend.tar
docker save mysql:8.0 -o mysql.tar
```

### 📤 2. Transfer Files

Transfer the following files to the target machine:

- `execl-backend.tar`
- `execl-frontend.tar`
- `mysql.tar`
- `docker-compose.yml`
- `backend/migration.sql`

### 📥 3. Import Images

On the target machine:

```bash
docker load -i mysql.tar
docker load -i execl-backend.tar
docker load -i execl-frontend.tar
```

### ✏️ 4. Modify docker-compose.yml

Change build instructions to use images:

```yaml
services:
  mysql:
    image: mysql:8.0
    # ... other config unchanged

  backend:
    image: execl-backend:latest  # Change from build to image
    # build: ./backend            # Comment out build
    # ... other config unchanged

  frontend:
    image: execl-frontend:latest  # Change from build to image
    # build: ./frontend            # Comment out build
    # ... other config unchanged
```

### 🚀 5. Start Services

```bash
docker-compose up -d
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

---

## 💻 Local Development Deployment

### 💾 1. Start MySQL

Quick start with Docker:

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

Or use locally installed MySQL and create database:

```sql
CREATE DATABASE excel_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### ⚡ 2. Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional, skip if using defaults)
# Windows:
set DATABASE_URL=mysql+pymysql://root:password@localhost:3306/excel_manager
# Linux/Mac:
export DATABASE_URL=mysql+pymysql://root:password@localhost:3306/excel_manager

# Start service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

📚 After backend starts, visit http://localhost:8000/docs to view API documentation.

### 🎨 3. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

🌐 After frontend starts, visit http://localhost:3000

---

## 💾 Database Information

### 📊 Table Structure

The system uses the following tables to store data:

| Table | Description |
|-------|------------|
| 👤 users | User information (username, email, password hash) |
| 🎫 sessions | User sessions (session_id, expiration time) |
| 📁 excel_files | Excel file info (includes original file binary data, user_id) |
| 📄 excel_sheets | Sheet information |
| 📝 excel_data | Cell data |
| 🔗 merged_cells | Merged cell information |
| 🖼️ sheet_images | Embedded image data (MEDIUMBLOB, max 16MB) |
| 📈 sheet_charts | Embedded chart information (JSON format) |
| 🗂️ table_regions | Table region information (multi-table support) |

### 🔄 Database Migration

To upgrade from v2.0 to v3.0 (adding user authentication), execute the database migration:

```bash
# Execute migration script
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

**⚠️ Note**:
- Migration script creates default user `migrated_user` (password: `default123`)
- Existing files will be associated with this default user
- Recommended to register new users after migration and delete the default user

### 🔧 Database Table Structure

```sql
-- Users table
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

-- Sessions table
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

-- Merged cells table
CREATE TABLE merged_cells (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sheet_id INT NOT NULL,
    start_row INT NOT NULL,
    start_col INT NOT NULL,
    end_row INT NOT NULL,
    end_col INT NOT NULL,
    FOREIGN KEY (sheet_id) REFERENCES excel_sheets(id) ON DELETE CASCADE
);

-- Images table
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

-- Charts table
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

-- Table regions table
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

## ⚙️ Production Configuration

### 🔐 Change Database Password

Edit `docker-compose.yml`:

```yaml
mysql:
  environment:
    MYSQL_ROOT_PASSWORD: your_secure_password  # Change this

backend:
  environment:
    DATABASE_URL: mysql+pymysql://root:your_secure_password@mysql:3306/excel_manager
```

### 🎫 Change Session Secret

```yaml
backend:
  environment:
    SESSION_SECRET: your-random-secret-key-min-32-chars  # Generate strong random key
```

Generate strong random key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 🌐 Change Ports

```yaml
frontend:
  ports:
    - "8080:80"  # Change 80 to another port

backend:
  ports:
    - "9000:8000"  # Change 8000 to another port
```

If backend port is changed, also update `frontend/nginx.conf`:

```nginx
location /api {
    proxy_pass http://backend:8000;  # Container internal port unchanged
}
```

### 💾 Data Persistence

MySQL data is stored in Docker volumes by default. View data volumes:

```bash
docker volume ls
```

Backup data:

```bash
docker exec excel-mysql mysqldump -uroot -ppassword excel_manager > backup.sql
```

Restore data:

```bash
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backup.sql
```

---

## ❓ Troubleshooting

### 🔌 1. Port Already in Use

```
Error: bind: address already in use
```

Solution:
- Modify port mappings in `docker-compose.yml`
- Or stop the service using the port

### 🗄️ 2. MySQL Connection Failed

```
Can't connect to MySQL server
```

Solution:
- Wait for MySQL to fully start (check `docker-compose logs mysql`)
- Verify DATABASE_URL configuration is correct

### 🌐 3. Frontend Cannot Access Backend API

Check proxy configuration in `frontend/nginx.conf`:

```nginx
location /api {
    proxy_pass http://backend:8000;
}
```

### 📤 4. File Upload Failed

- Check if file size exceeds 50MB
- Check if file format is .xls or .xlsx
- View backend logs: `docker-compose logs backend`
- Confirm logged in

### 🔐 5. Login Failed

- Confirm executed database migration script
- Check username and password are correct
- View backend logs: `docker-compose logs backend`

### ⏰ 6. Session Expired

- Session default validity is 24 hours
- Need to re-login after expiration
- Can adjust via SESSION_EXPIRE_HOURS environment variable

### 🔄 7. Merged Cells Display Incorrect

- Ensure using the latest frontend code
- Clear browser cache and refresh page
- Check backend logs for parsing errors

### 🖼️ 8. Images Not Displaying

- Confirm uploaded file is .xlsx format (.xls image extraction not supported)
- Check backend logs for image parsing errors
- Test image endpoint via API: `GET /api/images/{image_id}`
- Confirm user has permission to access the image

### 📥 9. File Download Failed

- Check backend logs for errors
- Chinese filenames use RFC 5987 encoding format; ensure backend is updated
- Confirm user has permission to access the file

### 📊 10. Pagination Switch to All Mode Failed

- Ensure backend `page_size` parameter limit is updated to 50000
- Rebuild backend image: `docker-compose build --no-cache backend`

### 🗑️ 11. Reset All Data

```bash
docker-compose down -v
docker-compose up -d --build
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

---

## 🔧 Service Management Commands

### 📊 Service Status
```bash
# View all service status
docker-compose ps

# View real-time logs
docker-compose logs -f [service_name]

# Restart service
docker-compose restart [service_name]

# Rebuild and start single service
docker-compose up -d --build backend
docker-compose up -d --build frontend

# Rebuild all services (without cache)
docker-compose build --no-cache
docker-compose up -d
```

### 🛠️ Container Operations
```bash
# Enter container
docker exec -it excel-backend /bin/bash
docker exec -it excel-frontend /bin/bash
docker exec -it excel-mysql mysql -uroot -ppassword

# Clean up unused images
docker image prune

# View container resource usage
docker stats
```

### 💾 Data Management
```bash
# Backup database
docker exec excel-mysql mysqldump -uroot -ppassword excel_manager > backup.sql

# Restore database
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backup.sql

# Execute database migration
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql

# View database size
docker exec excel-mysql mysql -uroot -ppassword -e "SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size in MB' FROM information_schema.tables WHERE table_schema='excel_manager';"
```

---

## ✨ Feature Documentation

### 🔐 Authentication Features

| Feature | Description |
|---------|-------------|
| 👤 User Registration | Username (3-50 chars), email validation, minimum 6-character password |
| 🔐 User Login | Session + Cookie authentication, 24-hour validity |
| 👋 User Logout | Clear server-side and client-side state |
| 🔒 Data Isolation | Users can only access their own files and data |

### 🚀 Supported Excel Features

| Feature | .xlsx | .xls |
|---------|-------|------|
| 📊 Cell data | ✅ | ✅ |
| 🔄 Merged cells | ✅ | ✅ |
| 🖼️ Embedded images | ✅ | ❌ |
| 📈 Embedded charts | ✅ (metadata) | ❌ |
| 📋 Multiple table regions | ✅ | ✅ |
| 🌐 Chinese filename download | ✅ | ✅ |
| 🔐 User data isolation | ✅ | ✅ |

### 🎨 Interface Description

#### 🔐 Login/Registration Page
- 📝 Dual forms with smooth switching
- 🎨 Gradient background with floating shapes
- ✨ Animation effects and micro-interactions
- 🎯 Form validation with user-friendly error messages

#### 📁 File List Page
- 👤 User info display with avatar
- 🌈 Gradient title effect
- 📤 Drag-and-drop upload with animations
- 📄 Beautiful file cards with transitions

#### 📊 Data View Page (Full-Screen)
- **🔧 Toolbar**: Back button, filename, Sheet selector, pagination toggle, download button
- **🖼️ Image/Chart Area** (collapsible): Embedded image thumbnails and chart info
- **📋 Data Table**:
  - 🔢 Row numbers fixed on left with gradient
  - 📑 Headers fixed at top with gradient
  - 🎭 Zebra stripes with gradient effects
  - ✨ Hover highlights with animations
  - 🔄 Merged cells with gradient background
  - 📊 Excel-style column letters (A, B, C, ..., AA, AB)
- **📊 Status Bar**: Row×Column count, current Sheet, pagination controls

### 🗂️ Multiple Table Region Detection

The system automatically splits table regions by identifying empty rows in a Sheet. When multiple data blocks separated by empty rows are detected, they are automatically identified as multiple table regions, allowing users to switch between them on the frontend.

### 📦 Dependency Package Description

#### ⚙️ Backend Dependencies (requirements.txt)
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `pymysql` - MySQL driver
- `cryptography` - MySQL 8.0 authentication support
- `passlib[bcrypt]` - bcrypt password hashing
- `openpyxl` - .xlsx file parsing
- `xlrd` - .xls file parsing
- `python-multipart` - File upload support

#### 🎨 Frontend Dependencies (package.json)
- `vue` - Vue 3 framework
- `vite` - Build tool
- `element-plus` - UI component library
- `pinia` - State management
- `axios` - HTTP client

---

<div align="center">
  <p>
    Made with ❤️ by Excel 管理专家团队
  </p>
  <p>
    <a href="#docker-deployment">🐳 Docker</a> •
    <a href="#local-development-deployment">💻 Local Dev</a> •
    <a href="#troubleshooting">❓ Troubleshooting</a>
  </p>
</div>