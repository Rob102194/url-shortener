from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, email: str, hashed_pwd: str) -> User:
        user = User(email=email, hashed_password=hashed_pwd)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
