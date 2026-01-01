"""认证相关 API 路由"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request

from ..database import get_db
from .. import crud, models, schemas
from ..config import SESSION_EXPIRE_HOURS, PASSWORD_MIN_LENGTH
from .auth import (
    hash_password,
    verify_password,
    create_session_id,
    get_current_user_optional
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserResponse,
             status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    if crud.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if crud.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 验证密码长度
    if len(user_data.password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"密码长度至少为{PASSWORD_MIN_LENGTH}位"
        )

    # 创建用户
    password_hash = hash_password(user_data.password)
    db_user = crud.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash
    )

    return schemas.UserResponse.model_validate(db_user)


@router.post("/login", response_model=schemas.SessionResponse)
async def login(
    user_data: schemas.UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """用户登录"""
    # 查找用户
    db_user = crud.get_user_by_username(db, user_data.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not verify_password(user_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 检查用户是否激活
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    # 清除旧会话
    crud.delete_user_sessions(db, db_user.id)

    # 创建新会话
    session_id = create_session_id()
    expires_at = datetime.now() + timedelta(hours=SESSION_EXPIRE_HOURS)
    crud.create_session(
        db=db,
        session_id=session_id,
        user_id=db_user.id,
        expires_at=expires_at
    )

    # 将 session_id 存储到 session cookie
    request.session["session_id"] = session_id

    return schemas.SessionResponse(
        access_token=session_id,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(db_user)
    )


@router.post("/logout", response_model=schemas.MessageResponse)
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """用户登出"""
    if current_user:
        # 从 session cookie 获取 session_id
        session_id = request.session.get("session_id")
        if session_id:
            crud.delete_session(db, session_id)

    # 清除 session
    request.session.clear()

    return schemas.MessageResponse(message="登出成功")


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user_optional)
):
    """获取当前用户信息"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录"
        )

    return schemas.UserResponse.model_validate(current_user)
