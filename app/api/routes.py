import logging
from fastapi import APIRouter, Depends, HTTPException
from app.service.task_service import TaskService
from app.api.schemas import TaskGetResponse, TaskCreateResponse
from app.api.dependencies import get_task_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks")


@router.post("", response_model=TaskCreateResponse)
async def create_task(service: TaskService = Depends(get_task_service)):
    try:
        task_id = await service.create_task()
        return TaskCreateResponse(id=task_id)
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskGetResponse)
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        task = await service.get_task_status(task_id)
        return TaskGetResponse(
            status=task.status.value,
            create_time=task.create_time,
            start_time=task.start_time,
            time_to_execute=task.exec_time
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))