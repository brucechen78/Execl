# Deployment Guide

This document describes the deployment methods for the Excel File Management System.

## Table of Contents

- [System Requirements](#system-requirements)
- [Docker Deployment (Recommended)](#docker-deployment-recommended)
- [Sideload Deployment](#sideload-deployment)
- [Local Development Deployment](#local-development-deployment)
- [Database Information](#database-information)
- [Production Configuration](#production-configuration)
- [Troubleshooting](#troubleshooting)
- [Service Management Commands](#service-management-commands)
- [Feature Documentation](#feature-documentation)

---

## System Requirements

### Docker Deployment

- Docker 20.10+
- Docker Compose 2.0+
- Available ports: 80 (frontend), 8000 (backend), 3306 (MySQL)

### Local Development

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

---

## Docker Deployment (Recommended)

### 1. Preparation

Ensure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

### 2. Start Services

```bash
cd Execl
docker-compose up -d --build
```

First startup requires image building and may take a few minutes.

### 3. Execute Database Migration

After starting services, execute the database migration script to add user authentication tables:

```bash
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

The migration script will:
- Create users table (user information)
- Create sessions table (user sessions)
- Modify excel_files table to add user_id foreign key
- Create default migration user (username: migrated_user, password: default123)
- Associate existing files with the default user

### 4. Verify Deployment

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

### 5. Access Application

| Service | Address |
|---------|---------|
| Frontend | http://localhost |
| API Documentation | http://localhost:8000/docs |
| MySQL | localhost:3306 |

### 6. First Login

1. Visit http://localhost
2. Login with default user or register a new user:
   - Default username: `migrated_user`
   - Default password: `default123`
3. After login, it's recommended to register a new user and delete the default user

### 7. Stop Services

```bash
# Stop services (keep data)
docker-compose down

# Stop services and remove data volumes
docker-compose down -v
```

---

## Sideload Deployment

Sideload deployment is useful for scenarios requiring offline deployment by exporting Docker images.

### 1. Build and Export Images

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

### 2. Transfer Files

Transfer the following files to the target machine:

- `execl-backend.tar`
- `execl-frontend.tar`
- `mysql.tar`
- `docker-compose.yml`

### 3. Import Images

On the target machine:

```bash
docker load -i mysql.tar
docker load -i execl-backend.tar
docker load -i execl-frontend.tar
```

### 4. Modify docker-compose.yml

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

### 5. Start Services

```bash
docker-compose up -d
```

---

## Local Development Deployment

### 1. Start MySQL

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

### 2. Start Backend

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

After backend starts, visit http://localhost:8000/docs to view API documentation.

### 3. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

After frontend starts, visit http://localhost:3000

---

## Database Information

The system uses the following tables to store data:

| Table | Description |
|-------|------------|
| users | User information (username, email, password hash) |
| sessions | User sessions (session_id, expiration time) |
| excel_files | Excel file info (includes original file binary data, user_id) |
| excel_sheets | Sheet information |
| excel_data | Cell data |
| merged_cells | Merged cell information |
| sheet_images | Embedded image data (MEDIUMBLOB, max 16MB) |
| sheet_charts | Embedded chart information (JSON format) |
| table_regions | Table region information (multi-table support) |

### Database Migration

To upgrade from v2.0 to v3.0 (adding user authentication), execute the database migration:

```bash
# Execute migration script
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

**Note**:
- Migration script creates default user `migrated_user` (password: `default123`)
- Existing files will be associated with this default user
- Recommended to register new users after migration and delete the default user

### Database Table Structure

```sql
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

## Production Configuration

### Change Database Password

Edit `docker-compose.yml`:

```yaml
mysql:
  environment:
    MYSQL_ROOT_PASSWORD: your_secure_password  # Change this

backend:
  environment:
    DATABASE_URL: mysql+pymysql://root:your_secure_password@mysql:3306/excel_manager
```

### Change Ports

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

### Data Persistence

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

## Troubleshooting

### 1. Port Already in Use

```
Error: bind: address already in use
```

Solution:
- Modify port mappings in `docker-compose.yml`
- Or stop the service using the port

### 2. MySQL Connection Failed

```
Can't connect to MySQL server
```

Solution:
- Wait for MySQL to fully start (check `docker-compose logs mysql`)
- Verify DATABASE_URL configuration is correct

### 3. Frontend Cannot Access Backend API

Check proxy configuration in `frontend/nginx.conf`:

```nginx
location /api {
    proxy_pass http://backend:8000;
}
```

### 4. File Upload Failed

- Check if file size exceeds 50MB
- Check if file format is .xls or .xlsx
- View backend logs: `docker-compose logs backend`

### 5. Merged Cells Display Incorrect

- Ensure using the latest frontend code
- Clear browser cache and refresh page
- Check backend logs for parsing errors

### 6. Images Not Displaying

- Confirm uploaded file is .xlsx format (.xls image extraction not supported)
- Check backend logs for image parsing errors
- Test image endpoint via API: `GET /api/images/{image_id}`

### 7. File Download Failed

- Check backend logs for errors
- Chinese filenames use RFC 5987 encoding format; ensure backend is updated

### 8. Pagination Switch to All Mode Failed

- Ensure backend `page_size` parameter limit is updated to 50000
- Rebuild backend image: `docker-compose build --no-cache backend`

### 9. Reset All Data

```bash
docker-compose down -v
docker-compose up -d --build
```

---

## Service Management Commands

```bash
# View status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Restart service
docker-compose restart [service_name]

# Rebuild and start single service
docker-compose up -d --build backend
docker-compose up -d --build frontend

# Rebuild all services (without cache)
docker-compose build --no-cache
docker-compose up -d

# Enter container
docker exec -it excel-backend /bin/bash
docker exec -it excel-mysql mysql -uroot -ppassword

# Clean up unused images
docker image prune
```

---

## Feature Documentation

### Supported Excel Features

| Feature | .xlsx | .xls |
|---------|-------|------|
| Cell data | ✅ | ✅ |
| Merged cells | ✅ | ✅ |
| Embedded images | ✅ | ❌ |
| Embedded charts | ✅ (metadata) | ❌ |
| Multiple table regions | ✅ | ✅ |
| Chinese filename download | ✅ | ✅ |

### Interface Description

#### File List Page
- Drag-drop upload area
- File list (filename, size, sheet count, upload time)
- Click row to enter data view page
- Download and delete buttons

#### Data View Page (Full-Screen)
- **Toolbar**: Back button, filename, Sheet selector, table region selector, pagination toggle, rows per page, download button
- **Image/Chart Area** (collapsible): Display embedded image thumbnails and chart information
- **Data Table**:
  - Row number column fixed on left
  - Header row fixed at top
  - Zebra stripes (alternating row colors)
  - Hover highlights
  - Merged cells (light yellow background)
  - Excel-style column letters (A, B, C, ..., AA, AB)
- **Status Bar**: Row × Column count, current Sheet, merged cell count, table region count, pagination controls

### Multiple Table Region Detection

The system automatically splits table regions by identifying empty rows in a Sheet. When multiple data blocks separated by empty rows are detected, they are automatically identified as multiple table regions, allowing users to switch between them on the frontend.

### Dependency Package Description

Backend dependencies (requirements.txt):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `pymysql` - MySQL driver
- `cryptography` - MySQL 8.0 authentication support
- `openpyxl` - .xlsx file parsing
- `xlrd` - .xls file parsing
- `python-multipart` - File upload support
