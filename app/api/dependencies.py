import logging
from fastapi import HTTPException, status
from app.service.task_service import TaskService
import app.main


logger = logging.getLogger(__name__)


async def get_task_service() -> TaskService:
    if app.main.task_service is None:
        logger.error("TaskService not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not initialized"
        )
    return app.main.task_service