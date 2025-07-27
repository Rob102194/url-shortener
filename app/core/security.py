from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- hashing ----
def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return pwd_ctx.verify(pw, hashed)

# ---- tokens ----
def _create_token(sub: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": sub}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(user_id: str) -> str:
    return _create_token(
        sub=user_id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(user_id: str) -> str:
    return _create_token(
        sub=user_id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
