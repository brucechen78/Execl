import os

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/excel_manager"
)

# 文件上传配置
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".xls", ".xlsx"}

# Session 配置
SESSION_SECRET = os.getenv("SESSION_SECRET", "excel-manager-secret-key-change-in-production-2024")
SESSION_EXPIRE_HOURS = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))  # 24小时过期

# 密码配置
PASSWORD_MIN_LENGTH = 6
