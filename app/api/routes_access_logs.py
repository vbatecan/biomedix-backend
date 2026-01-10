import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import database
from app.database.schemas import AccessLogSchema, CreateAccessLogSchema
from app.services.access_log_service import AccessLogService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=AccessLogSchema)
async def create_access_log(
    log_data: CreateAccessLogSchema,
    db: AsyncSession = Depends(database.get_db)
):
    try:
        return await AccessLogService.create_access_log(db, log_data)
    except Exception as e:
        logger.error(f"Error creating access log: {e}")
        raise HTTPException(status_code=500, detail="Failed to create access log")


@router.get("/", response_model=List[AccessLogSchema])
async def get_access_logs(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(database.get_db)
):
    try:
        return await AccessLogService.get_access_logs(db, limit, offset)
    except Exception as e:
        logger.error(f"Error fetching access logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch access logs")
