from pydantic import BaseModel, Field
from datetime import datetime
from app.domain.task import TaskStatus


class TaskCreateResponse(BaseModel):
    id: int


class TaskGetResponse(BaseModel):
    status: TaskStatus
    create_time: datetime
    start_time: datetime | None
    time_to_execute: float | None
    
