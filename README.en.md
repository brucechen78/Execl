# 🎉 Excel File Management System

A web-based Excel file management system with **youthful design**, supporting multi-user access, user authentication, upload, storage, viewing, downloading, and deleting of Excel files with complete data isolation between users.

![Excel Expert](https://img.shields.io/badge/Excel-Management-Expert-brightgreen?style=for-the-badge&logo=microsoft-excel)
![Vue](https://img.shields.io/badge/Vue-3-4FC08D?style=for-the-badge&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)

## ✨ Features

### 🔐 Authentication
- **👤 User Registration**: Username and email registration, minimum 6-character password
- **🔐 User Login**: Session + Cookie authentication, 24-hour validity
- **👋 User Logout**: Clear server-side and client-side state
- **🔒 Data Isolation**: Users can only access their own files and data

### 🚀 Core Features
- **📤 File Upload**: Support for .xls and .xlsx formats with drag-and-drop or click-based upload, files linked to current user
- **💾 File Storage**: Original file binary storage + structured parsed data storage with user-level data isolation
- **👀 Data Display**: Full-screen table display with pagination/all-data toggle, multi-Sheet switching, only shows current user's files
- **📁 File Management**: File list display (current user only), file download, file deletion

### 🎨 Advanced Features
- **🔄 Merged Cells**: Correct parsing and rendering of merged cells in Excel (gradient highlight)
- **🖼️ Embedded Images**: Extract and display images from Excel with preview support on click
- **📈 Embedded Charts**: Identify chart types and location information
- **🗂️ Multiple Table Regions**: Auto-detect multiple tables within a single Sheet (separated by empty rows) with switching support

### 🌈 Interface Features
- **💫 Youthful Theme**: Vibrant gradients, rounded corners, smooth animations
- **🎭 Modern Design**: Glass-morphism effects, floating animations, shadow layers
- **📱 Responsive Layout**: Perfect for desktop and mobile devices
- **✨ Interactive Experience**: Hover effects, transition animations, micro-interactions

## 🎭 Interface Preview

### 🔐 Login/Registration Page
- **📝 Dual Forms**: User login and registration forms with smooth switching
- **🎨 Gradient Background**: Vibrant blue-purple gradient background
- **✨ Animation Effects**: Floating decorative shapes, dynamic atmosphere
- **🎯 Form Validation**: Real-time validation with user-friendly error messages

### 📁 File List Page
- **🎭 Modern Navigation**: User avatar, username, and role display
- **🌈 Gradient Title**: "Excel Management Expert" with gradient text effect
- **📤 Card Upload**: Drag-and-drop upload with floating animation
- **📄 Beautiful List**: File display with cards, shadows, and transitions

### 📊 Data View Page (Full-Screen)
- **🌈 Gradient Headers**: Blue-purple gradient table headers with white text
- **🎨 Colorful Row Numbers**: Pink-orange gradient row number column
- **✨ Floating Effects**: Rows subtly lift on hover with shadow effects
- **🔧 Glass Toolbar**: Semi-transparent background, blur effect, ultra-modern
- **✨ Animated Status Bar**: Pulse animation effect when displaying all data

## 🛠 Technology Stack

| Layer | Technology |
|-------|-----------|
| 🎨 Frontend | Vue 3 + Vite + Element Plus + Pinia |
| ⚡ Backend | Python + FastAPI + SQLAlchemy + Passlib |
| 🗄️ Database | MySQL 8.0 |
| 🐳 Deployment | Docker + Docker Compose |
| 🔐 Authentication | Session + Cookie + bcrypt |
| 🎯 UI Design | CSS custom properties, gradients, animations, glass-morphism |

## 📁 Project Structure

```
├── backend/                # Backend service
│   ├── app/
│   │   ├── main.py        # FastAPI entry
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database connection
│   │   ├── models.py      # Data models (User, Session, Excel)
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── crud.py        # Database operations
│   │   ├── auth.py        # Authentication utilities
│   │   └── routers/
│   │       ├── auth.py    # Authentication API routes
│   │       └── excel.py   # Excel API routes
│   ├── requirements.txt
│   ├── migration.sql      # Database migration script
│   └── Dockerfile
├── frontend/              # Frontend service
│   ├── src/
│   │   ├── App.vue        # Main application (includes auth flow)
│   │   ├── main.js
│   │   ├── stores/
│   │   │   └── auth.js    # Auth state management (Pinia)
│   │   ├── api/
│   │   │   ├── auth.js    # Authentication API
│   │   │   └── excel.js   # Excel API (with auth interceptors)
│   │   └── components/
│   │       ├── Login.vue      # Login component
│   │       ├── Register.vue   # Registration component
│   │       ├── FileUpload.vue # Upload component
│   │       ├── FileList.vue   # File list
│   │       └── DataTable.vue  # Data table (full-screen)
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── README.md              # 🇨🇳 Chinese documentation
├── README.en.md          # 🇺🇸 English documentation
├── DEPLOYMENT.md         # 🇨🇳 Chinese deployment guide
└── DEPLOYMENT.en.md     # 🇺🇸 English deployment guide
```

## 🗄️ Database Models

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

## 🚀 Quick Start

### 🐳 Using Docker (Recommended)

```bash
# Navigate to project directory after cloning
cd Execl

# Start all services
docker-compose up -d --build

# Execute database migration (add user authentication tables)
docker exec -i excel-mysql mysql -uroot -ppassword excel_manager < backend/migration.sql
```

🎉 First startup requires building images, which may take a few minutes.

### ✅ Verify Deployment

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

All services should show `running` status:

```
NAME              STATUS
excel-mysql      running (healthy)
excel-backend    running
excel-frontend   running
```

### 🌐 Access Application

| Service | URL | Description |
|---------|-----|-------------|
| 🎨 Frontend | http://localhost | Youthful style interface |
| 📚 API Docs | http://localhost:8000/docs | Backend API documentation |
| 💾 MySQL | localhost:3306 | Database service |

### 👤 First Login

1. 🌐 Visit http://localhost
2. 🔐 Use default user or register new user:
   - 📝 Default username: `migrated_user`
   - 🔑 Default password: `default123`
3. 🎯 After login, recommend registering new user and deleting default user

### 🛑 Stop Services

```bash
# Stop services (keep data)
docker-compose down

# Stop services and remove data volumes
docker-compose down -v
```

## 🔌 API Endpoints

### 🔐 Authentication API

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | User registration |
| POST | /api/auth/login | User login |
| POST | /api/auth/logout | User logout |
| GET | /api/auth/me | Get current user info |

### 📁 File API (Requires Authentication)

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/upload | Upload Excel file |
| GET | /api/files | Get current user's file list |
| GET | /api/files/{id} | Get file details |
| GET | /api/files/{id}/sheets/{sheet_id}/data | Get Sheet data (with merged cells, images, charts, table regions) |
| GET | /api/files/{id}/download | Download file (supports Chinese filenames) |
| GET | /api/images/{image_id} | Get image binary data |
| DELETE | /api/files/{id} | Delete file |

### 📊 Sheet Data Response Structure

```json
{
  "sheet_id": 1,
  "sheet_name": "Sheet1",
  "total_rows": 100,
  "total_columns": 10,
  "page": 1,
  "page_size": 50,
  "headers": ["Column1", "Column2", "..."],
  "data": [["Value1", "Value2", "..."], "..."],
  "merged_cells": [
    {"start_row": 0, "start_col": 0, "end_row": 1, "end_col": 2}
  ],
  "images": [
    {"id": 1, "image_format": "png", "anchor_row": 5, "anchor_col": 3, "width": 200, "height": 150}
  ],
  "charts": [
    {"id": 1, "chart_type": "bar", "chart_title": "Sales Chart", "anchor_row": 10, "anchor_col": 0}
  ],
  "table_regions": [
    {"id": 1, "region_index": 0, "start_row": 0, "end_row": 20, "table_name": "Table1"},
    {"id": 2, "region_index": 1, "start_row": 25, "end_row": 50, "table_name": "Table2"}
  ]
}
```

## ⚙️ Configuration

### 🌍 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | mysql+pymysql://root:password@localhost:3306/excel_manager | Database connection string |
| SESSION_SECRET | excel-manager-secret-key-change-in-production-2024 | Session encryption key |
| SESSION_EXPIRE_HOURS | 24 | Session validity period (hours) |

### 📁 File Limits

- 🎯 Maximum file size: 50MB
- 📄 Supported formats: .xls, .xlsx
- 📊 Pagination mode: 20/50/100/200/500 rows per page
- 🔄 All mode: Up to 50,000 rows

## 💡 Feature Description

### 🔐 Authentication Flow

1. **📝 Registration**: User fills in username, email, password. Auto-login after successful registration
2. **🔐 Login**: Login with username/password. Server creates Session and returns token
3. **🔒 Authentication**: All API requests carry token. Server verifies user identity
4. **👋 Logout**: Clear server-side Session and client-side state

### 🛡️ Data Isolation

- Each user can only access their own uploaded files
- File upload automatically associates with current user ID
- All API requests verify user permissions
- Image download also verifies file ownership

### 🎨 Table Display

- **🖥️ Full-Screen Display**: Click a file to enter full-screen data view
- **🎭 Zebra Stripes**: Alternating row colors with gradient effects
- **✨ Hover Highlight**: Hovering row with shadow and animation effects
- **📊 Column Letters**: Each column shows Excel-style column letters (A, B, C, ..., AA, AB)
- **🔢 Fixed Row Numbers**: Row number column fixed on the left with gradient background
- **📑 Fixed Header**: Header row fixed at the top with gradient background

### 🌈 Merged Cells

- Automatically parsed when uploading
- Frontend uses native HTML table colspan/rowspan for correct rendering
- Merged cells highlighted with gradient background and floating animation

### 🖼️ Embedded Images

- Support for images embedded in .xlsx format
- Images stored in database, retrieved via API
- Frontend displays image thumbnails with preview on click
- Shows image anchor position in Excel (e.g., A1, B5)

### 📈 Embedded Charts

- Recognize common chart types: bar, line, pie, area, scatter, etc.
- Display chart title and anchor position
- Note: Currently shows chart metadata only, no visual rendering

### 🗂️ Multiple Table Regions

- Auto-detect multiple tables separated by empty rows in a single Sheet
- Toolbar displays table region selector
- Choose to view all data or specific table region
- Table name automatically extracted from first row's first non-empty cell

## ⚠️ Notes

- `.xls` format image and chart extraction not yet supported (xlrd library limitation)
- Charts currently show metadata only, no visual rendering
- Large files recommended to use pagination mode
- Chinese filename downloads use RFC 5987 encoding format
- All API requests require user authentication
- Re-login required after Session expiration

## 🔒 Security Notes

- Passwords encrypted with bcrypt
- Session ID generated using cryptographically secure random string
- Complete data isolation between users
- Recommended to change SESSION_SECRET in production environment

## 📜 License

MIT License

---

<div align="center">
  <p>
    Made with ❤️ by Excel 管理专家团队
  </p>
  <p>
    <a href="#quick-start">🚀 Quick Start</a> •
    <a href="#features">✨ Features</a> •
    <a href="#api-endpoints">🔌 API</a>
  </p>
</div>