# Excel File Management System

A web-based Excel file management system that supports uploading, storing, viewing, downloading, and deleting Excel files.

## Features

- **File Upload**: Support for .xls and .xlsx formats with drag-and-drop or click-based upload
- **File Storage**: Original file binary storage + structured parsed data storage
- **Data Display**: Full-screen table display with pagination/all-data toggle, multi-Sheet switching
- **Zebra Striping**: Alternating row colors with hover highlights and Excel-style column letters
- **File Download**: Support for downloading files with Chinese filenames
- **File Deletion**: Delete files and associated data
- **Merged Cells**: Correct parsing and rendering of merged cells in Excel (light yellow highlight)
- **Embedded Images**: Extract and display images from Excel with preview support on click
- **Embedded Charts**: Identify chart types and location information
- **Multiple Table Regions**: Auto-detect multiple tables within a single Sheet (separated by empty rows) with switching support

## Interface Preview

### File List Page
- Drag-drop upload area
- File list (filename, size, sheet count, upload time)
- Support for download and delete operations

### Data View Page (Full-Screen)
- Top toolbar: Back button, filename, Sheet selector, table region selector, pagination toggle, download button
- Image/chart display area (collapsible)
- Full-screen data table: Fixed row numbers, fixed header, zebra stripes, hover highlights
- Bottom status bar: Row×Column count, current Sheet, merged cell count, table region count, pagination controls

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Vite + Element Plus |
| Backend | Python + FastAPI + SQLAlchemy |
| Database | MySQL 8.0 |
| Deployment | Docker + Docker Compose |

## Project Structure

```
├── backend/                # Backend service
│   ├── app/
│   │   ├── main.py        # FastAPI entry
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database connection
│   │   ├── models.py      # Data models
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── crud.py        # Database operations
│   │   └── routers/
│   │       └── excel.py   # API routes
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # Frontend service
│   ├── src/
│   │   ├── App.vue        # Main application (page routing)
│   │   ├── main.js
│   │   ├── api/
│   │   │   └── excel.js   # API wrapper
│   │   └── components/
│   │       ├── FileUpload.vue  # Upload component
│   │       ├── FileList.vue    # File list
│   │       └── DataTable.vue   # Data table (full-screen)
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── README.md
└── DEPLOYMENT.md          # Detailed deployment guide
```

## Database Models

The system uses the following tables to store Excel data:

| Table | Description |
|-------|------------|
| excel_files | Excel file info (includes original file binary) |
| excel_sheets | Sheet information |
| excel_data | Cell data |
| merged_cells | Merged cell information |
| sheet_images | Embedded image data |
| sheet_charts | Embedded chart information |
| table_regions | Table region information (multi-table support) |

## Quick Start

### Using Docker (Recommended)

```bash
# Navigate to project directory after cloning
cd Execl

# Start all services
docker-compose up -d --build

# Check service status
docker-compose ps
```

After startup, access:
- Frontend: http://localhost
- API Documentation: http://localhost:8000/docs

### Stop Services

```bash
docker-compose down
```

### Rebuild Database

If upgrading from an older version, rebuild the database to create new tables:

```bash
# Stop services and remove data volumes
docker-compose down -v

# Restart
docker-compose up -d --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/upload | Upload Excel file |
| GET | /api/files | Get file list |
| GET | /api/files/{id} | Get file details |
| GET | /api/files/{id}/sheets/{sheet_id}/data | Get Sheet data (with merged cells, images, charts, table regions) |
| GET | /api/files/{id}/download | Download file (supports Chinese filenames) |
| GET | /api/images/{image_id} | Get image binary data |
| DELETE | /api/files/{id} | Delete file |

### Sheet Data Response Structure

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

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | mysql+pymysql://root:password@localhost:3306/excel_manager | Database connection string |

### File Limits

- Maximum file size: 50MB
- Supported formats: .xls, .xlsx
- Pagination mode: 20/50/100/200/500 rows per page
- All mode: Up to 50,000 rows

## Feature Description

### Table Display

- **Full-Screen Display**: Click a file to enter full-screen data view
- **Zebra Stripes**: Alternating row colors (white/light gray)
- **Hover Highlight**: Hovering row becomes light blue
- **Column Letters**: Each column shows Excel-style column letters (A, B, C, ..., AA, AB)
- **Fixed Row Numbers**: Row number column fixed on the left
- **Fixed Header**: Header row fixed at the top

### Merged Cells

- Automatically parsed when uploading
- Frontend uses native HTML table colspan/rowspan for correct rendering
- Merged cells highlighted with light yellow background

### Embedded Images

- Support for images embedded in .xlsx format
- Images stored in database, retrieved via API
- Frontend displays image thumbnails with preview on click
- Shows image anchor position in Excel (e.g., A1, B5)

### Embedded Charts

- Recognize common chart types: bar, line, pie, area, scatter, etc.
- Display chart title and anchor position
- Note: Currently shows chart metadata only, no visual rendering

### Multiple Table Regions

- Auto-detect multiple tables separated by empty rows in a single Sheet
- Toolbar displays table region selector
- Choose to view all data or specific table region
- Table name automatically extracted from first row's first non-empty cell

## Notes

- `.xls` format image and chart extraction not yet supported (xlrd library limitation)
- Charts currently show metadata only, no visual rendering
- Large files recommended to use pagination mode
- Chinese filename downloads use RFC 5987 encoding format

## License

MIT License
