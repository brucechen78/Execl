-- 认证和用户隔离数据库迁移脚本
-- 执行前请备份数据库

-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 创建会话表
CREATE TABLE IF NOT EXISTS sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 修改 excel_files 表，添加 user_id 列
-- 首先添加可空的 user_id 列
ALTER TABLE excel_files ADD COLUMN user_id INT NULL AFTER id;

-- 4. 创建默认用户用于迁移现有数据
-- 密码为 'default123' (bcrypt hash)
INSERT INTO users (username, email, password_hash, is_active)
VALUES ('migrated_user', 'migrated@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', TRUE)
ON DUPLICATE KEY UPDATE id=id;

-- 5. 将现有文件关联到默认用户
UPDATE excel_files SET user_id = (SELECT id FROM users WHERE username = 'migrated_user')
WHERE user_id IS NULL;

-- 6. 修改列属性为 NOT NULL
ALTER TABLE excel_files MODIFY COLUMN user_id INT NOT NULL;

-- 7. 添加外键约束
ALTER TABLE excel_files
ADD CONSTRAINT fk_excel_files_user
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 8. 添加索引
CREATE INDEX idx_excel_files_user_id ON excel_files(user_id);

-- 迁移完成
-- 注意：默认用户名为 'migrated_user'，密码为 'default123'
-- 登录后请及时修改密码或创建新用户
