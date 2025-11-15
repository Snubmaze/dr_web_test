from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class TaskStatus(Enum):
    IN_QUEUE = "In queue"
    RUN = "Run"
    COMPLETED = "Completed"


@dataclass
class Task:
    id: int
    status: TaskStatus
    create_time: datetime
    start_time: Optional[datetime] = None
    exec_time: Optional[float] = None

    def mark_as_running(self) -> None:
        if self.status != TaskStatus.IN_QUEUE:
            raise ValueError(f"Cannot run task with status: {self.status}")
        self.status = TaskStatus.RUN
        self.start_time = datetime.now()

    def mark_as_completed(self, exec_time) -> None:
        if self.status != TaskStatus.RUN:
            raise ValueError(f"Cannot run task with status: {self.status}")
        self.status = TaskStatus.COMPLETED
        self.exec_time = exec_time
