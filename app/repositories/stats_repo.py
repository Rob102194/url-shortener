from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.link import Link, LinkStats

class StatsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_stats(self, short_code: str):
        stmt = (
            select(LinkStats)
            .join(Link)
            .where(Link.short_code == short_code)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
