from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.repositories.user_repo import UserRepository

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, email: str, password: str):
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed = pwd_ctx.hash(password)
        return await self.user_repo.create(email, hashed)
