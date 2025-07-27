from fastapi import HTTPException, status
from app.repositories.user_repo import UserRepository
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_password,
)
from app.core.cache import CacheManager
from app.core.config import settings

class AuthService:
    def __init__(self, user_repo: UserRepository, cache: CacheManager):
        self.repo = user_repo
        self.cache = cache

    async def register(self, email: str, password: str):
        existing_user = await self.repo.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed = hash_password(password)
        return await self.repo.create(email, hashed)

    async def login(self, email: str, password: str):
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )
        return {
            "access_token": create_access_token(str(user.id)),
            "refresh_token": create_refresh_token(str(user.id)),
        }

    async def logout(self, refresh_token: str):
        await self.cache.add_to_blacklist(
            refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
