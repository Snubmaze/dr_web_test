import logging
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.domain.task import Task, TaskStatus
from app.infrastructure.models import TaskModel


logger = logging.getLogger(__name__)


class TaskRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db


    async def save_task(self) -> Task:
        task_model = TaskModel(
            status = TaskStatus.IN_QUEUE.value,
            create_time = datetime.now()
        )

        self.db.add(task_model)
        await self.db.commit()
        await self.db.refresh(task_model)

        return self._model_to_domain(task_model)
    

    async def get_task(self, task_id: int, refresh: bool = False) -> Task:
        result = await self.db.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model = result.scalar_one_or_none()
        
        if not task_model:
            raise ValueError(f"Task {task_id} not found")
        
        if refresh:
            await self.db.refresh(task_model)
        
        return self._model_to_domain(task_model)
    

    async def update_task(self, task: Task) -> Task:
        result = await self.db.execute(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        task_model = result.scalar_one_or_none()
        
        if not task_model:
            raise ValueError(f"Task {task.id} not found")
        
        task_model.status = task.status.value
        task_model.start_time = task.start_time
        task_model.exec_time = task.exec_time
        
        await self.db.commit()
        await self.db.refresh(task_model)
        
        logger.debug(f"Task {task.id} updated in DB: status={task.status.value}, exec_time={task.exec_time}")
        
        return self._model_to_domain(task_model)
    

    async def clear_all_tasks(self) -> None:
        await self.db.execute(delete(TaskModel))
        await self.db.commit()
        logger.info("All tasks cleared from database")
    

    @staticmethod
    def _model_to_domain(model: TaskModel) -> Task:
        return Task(
            id=model.id,
            status=TaskStatus(model.status),
            create_time=model.create_time,
            start_time=model.start_time,
            exec_time=model.exec_time
        )