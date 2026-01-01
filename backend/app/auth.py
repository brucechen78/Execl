"""认证工具函数"""
from typing import Optional
from datetime import datetime, timedelta
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.requests import Request

from .database import get_db
from . import models, crud
from .config import SESSION_EXPIRE_HOURS

security = HTTPBearer(auto_error=False)

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """使用 bcrypt 哈希密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_session_id() -> str:
    """生成随机 session ID"""
    return secrets.token_urlsafe(32)


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPBearer = Depends(security)
) -> Optional[models.User]:
    """
    获取当前用户（可选）
    如果未登录返回 None，而不是抛出异常
    """
    # 优先从 Authorization header 获取 token
    if credentials:
        session_id = credentials.credentials
    else:
        # 从 session cookie 获取
        session_id = request.session.get("session_id")

    if not session_id:
        return None

    # 验证 session
    db_session = crud.get_session_by_id(db, session_id)
    if not db_session:
        return None

    # 获取用户
    user = crud.get_user_by_id(db, db_session.user_id)
    if not user or not user.is_active:
        return None

    return user


async def get_current_user(
    current_user: models.User = Depends(get_current_user_optional)
) -> models.User:
    """
    获取当前用户（必需）
    如果未登录抛出 401 异常
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
