from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.stats_service import StatsService
from app.repositories.stats_repo import StatsRepository

router = APIRouter(prefix="/stats", tags=["stats"])

def get_stats_repo(db: AsyncSession = Depends(get_db)) -> StatsRepository:
    return StatsRepository(db)

def get_stats_service(
    repo: StatsRepository = Depends(get_stats_repo)
) -> StatsService:
    return StatsService(repo)

@router.get("/{short_code}")
async def get_stats(
    short_code: str, service: StatsService = Depends(get_stats_service)
):
    return await service.get_stats(short_code)


@router.post("/{short_code}/click")
async def record_click(
    short_code: str, service: StatsService = Depends(get_stats_service)
):
    # Aquí se podría registrar un clic en la base de datos
    # Por simplicidad, solo se invalida el caché
    await service.invalidate_stats_cache(short_code)
    return {"message": "Click recorded and cache invalidated"}
