from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from database.userOperation import create_user, delete_user, getById, getByName
from model.user import UserCreate, UserOut
from util.authUtil import create_access_token, examine_password, examine_username, get_password_hash, verify_password, \
    verify_token

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    :param user_in: 用户注册信息
    :param db:
    :return: 注册成功的用户对象
    """
    if user_in.username == "" or user_in.password == "":
        raise HTTPException(status_code=400, detail="用户名或密码不能为空")
    if getByName(db, user_in.username):
        raise HTTPException(status_code=400, detail="用户名已被注册")
    if not examine_username(user_in.username):
        raise HTTPException(status_code=400, detail="用户名不符合规范")
    if not examine_password(user_in.password, level=0):
        raise HTTPException(status_code=400, detail="密码不符合规范")
    hashed_pw = get_password_hash(user_in.password)
    user = create_user(db, user_in.username, hashed_pw, role=user_in.role)
    return user


@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口
    :param form_data:自动从请求体中提取用户名和密码
    :param db:数据库会话，依赖注入
    :return:包含 access_token 和 token_type 的字典（用于后续身份认证）
    """
    user = getByName(db, form_data.username)
    if form_data.username == "" or form_data.password == "":
        raise HTTPException(status_code=400, detail="用户名或密码不能为空")
    if not user:
        raise HTTPException(status_code=401, detail="请先注册")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/login")),
                     db: Session = Depends(get_db)):
    """
    依赖注入函数， 获取当前登录用户对象
    :param token:从请求头Authorization中自动解析的JWT令牌
    :param db: 数据库会话，依赖注入
    :return: 当前登录用户对象
    """
    token_data = verify_token(token)
    user_id = token_data.get("user_id")

    if user_id == "EXPIRED":
        raise HTTPException(status_code=401, detail="登录状态已过期，请重新登录")
    if user_id is None:
        raise HTTPException(status_code=401, detail="非法身份信息")

    user = getById(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="未找到用户")
    return user


@auth_router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    """
    获取当前登录用户信息
    :param current_user: 当前登录用户对象
    :return: 当前登录用户对象
    """
    return current_user


@auth_router.delete("/delete/{user_id}")
def delete_user_by_id(
        user_id: int = Path(..., title="要删除的用户ID"),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限删除用户")
    if current_user.id == user_id and current_user.role != "super":
        raise HTTPException(status_code=403, detail="不能删除自己")
    deleted_user = delete_user(db, user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="用户不存在或已删除")
    return {"message": f"删除id为 {user_id}的用户成功,删除者为：{current_user.username}"}


@auth_router.get("/user/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int = Path(..., title="要获取的用户ID"), db: Session = Depends(get_db)):
    user = getById(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@auth_router.get("/user", response_model=UserOut)
def get_user_by_name(username: str = Query(..., title="用户名"), db: Session = Depends(get_db)):
    user = getByName(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
