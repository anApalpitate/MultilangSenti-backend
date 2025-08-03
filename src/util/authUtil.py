import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "JiNiTaiMei"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 一个星期
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建JWT访问令牌
    :param data: 包含要编码进JWT负载的字典数据（如用户标识）
    :param expires_delta: 可选的过期时间间隔，如果未指定则默认使用ACCESS_TOKEN_EXPIRE_MINUTES
    :return: 生成的JWT字符串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    校验 JWT 令牌是否有效并解析用户ID
    :param token: 待校验的 JWT 字符串
    :return: 合法则返回用户ID字符串，非法或过期返回 None 或 "EXPIRED"
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": user_id, "role": payload.get("role")}
    except ExpiredSignatureError:
        return "EXPIRED"
    except JWTError:
        return None


def get_password_hash(password):
    """
    对明文密码进行哈希加密
    :param password: 待加密密码
    :return: 加密后的哈希密码字符串
    """
    return pwd_context.hash(password)


def verify_password(password, hashed_password):
    """
    验证用户输入密码是否与哈希密码匹配
    :param password: 用户输入的明文密码
    :param hashed_password: 数据库中存储的哈希密码
    :return: 验证成功返回True，失败返回False
    """
    return pwd_context.verify(password, hashed_password)


def examine_password(password: str, level: int = 0) -> bool:
    """
    检查密码是否符合要求
    :param password: 待检查密码
    :param level: 复杂度级别（0：6-20位，1：8-20位+字母数字，2：8-20位+数字+小写/大写/特殊中任意两种）
    :return: True 合格，False 不合格
    """
    length = len(password)
    if level == 0:
        return 6 <= length <= 20
    if length < 8 or length > 20:
        return False
    if level == 1:
        return bool(re.search(r'[A-Za-z]', password)) and bool(re.search(r'\d', password))
    if level == 2:
        digit = bool(re.search(r'\d', password))
        types = sum(bool(re.search(p, password)) for p in [r'[a-z]', r'[A-Z]', r'[^A-Za-z0-9]'])
        return digit and types >= 2
    return False


def examine_username(username: str) -> bool:
    """
    检查用户名是否符合要求：
    - 长度在 4~30 个字符之间
    - 不能以下划线开头
    :param username: 待检查用户名
    :return: True 合格，False 不合格
    """
    return 4 <= len(username) <= 30 and not username.startswith("_")
