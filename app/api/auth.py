from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.core.db import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_auth_service(repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(repo)

@router.post("/register", status_code=201)
async def register(
    req: RegisterRequest, service: AuthService = Depends(get_auth_service)
):
    user = await service.register(req.email, req.password)
    return {"id": user.id, "email": user.email}
