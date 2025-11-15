import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.infrastructure.database import init_db, AsyncSessionLocal
from app.infrastructure.repository import TaskRepository
from app.core.queue import Queue
from app.service.task_service import TaskService
from app.api.routes import router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

queue: Queue = Queue()
task_service: TaskService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация БД и запуск фонового воркера при старте"""
    global task_service
    
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")
    
    async with AsyncSessionLocal() as session:
        repo = TaskRepository(session)
        await repo.clear_all_tasks()
    
    task_service = TaskService(queue)
    
    executor_task = asyncio.create_task(task_service.start_task_executor())
    logger.info("Task executor started")
    
    yield
    
    logger.info("Shutting down...")
    executor_task.cancel()
    try:
        await executor_task
    except asyncio.CancelledError:
        pass
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Task Queue Service",
    lifespan=lifespan
)

app.include_router(router)