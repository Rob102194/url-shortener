from passlib.context import CryptContext
from app.repositories.user_repo import UserRepository

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, email: str, password: str):
        hashed = pwd_ctx.hash(password)
        return await self.user_repo.create(email, hashed)
