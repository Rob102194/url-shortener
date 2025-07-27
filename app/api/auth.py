from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.core.db import get_db
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository
from app.api.auth_schemas import LoginRequest, TokenResponse, RefreshRequest
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from jose import jwt, JWTError
from app.core.cache import get_cache_manager, CacheManager

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_auth_service(
    repo: UserRepository = Depends(get_user_repo),
    cache: CacheManager = Depends(get_cache_manager),
) -> AuthService:
    return AuthService(repo, cache)

@router.post("/register", response_model=TokenResponse)
async def register(
    req: RegisterRequest, service: AuthService = Depends(get_auth_service)
):
    await service.register(req.email, req.password)
    tokens = await service.login(req.email, req.password)
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    tokens = await service.login(body.email, body.password)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    user_repo: UserRepository = Depends(get_user_repo),
    cache: CacheManager = Depends(get_cache_manager),
):
    if await cache.is_blacklisted(body.refresh_token):
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    try:
        payload = jwt.decode(
            body.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido")

    # Chequear si el usuario existe
    user = await user_repo.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    # Refresh token antiguo a la blacklist
    await cache.add_to_blacklist(
        body.refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/logout")
async def logout(
    body: RefreshRequest, service: AuthService = Depends(get_auth_service)
):
    await service.logout(body.refresh_token)
    return {"message": "Logout successful"}
