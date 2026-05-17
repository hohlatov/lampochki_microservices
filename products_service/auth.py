# products_service/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from pydantic import BaseModel

# ---------- Конфигурация ----------
SECRET_KEY = "your-super-secret-key-change-in-production-12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security схема для Bearer token
security = HTTPBearer()

# ---------- Модели ----------
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

# ---------- Временная "база" администраторов ----------
# В реальном проекте — таблица в БД
ADMINS = {
    "admin": {
        "username": "admin",
        "password": pwd_context.hash("admin123"),  # пароль: admin123
        "role": "admin"
    },
    "manager": {
        "username": "manager",
        "password": pwd_context.hash("manager123"),
        "role": "manager"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    if username not in ADMINS:
        return None
    user = ADMINS[username]
    if not verify_password(password, user["password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Зависимость для защиты эндпоинтов"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        if username not in ADMINS:
            raise credentials_exception
        return ADMINS[username]
    except JWTError:
        raise credentials_exception

def get_current_admin(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        role = payload.get("role")

        if role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Forbidden"
            )

        return payload

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )