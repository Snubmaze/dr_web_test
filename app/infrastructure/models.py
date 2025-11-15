from app.infrastructure.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(nullable=False)
    create_time: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())
    start_time: Mapped[datetime] = mapped_column(nullable=True)
    exec_time: Mapped[float] = mapped_column(nullable=True)