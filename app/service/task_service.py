import asyncio
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor
from app.core.queue import Queue
from app.infrastructure.repository import TaskRepository
from app.infrastructure.database import AsyncSessionLocal
from app.domain.task import Task

logger = logging.getLogger(__name__)


class TaskService:
    MAX_CONCURRENT_TASKS = 2
    
    def __init__(self, queue: Queue):
        self._queue = queue
        self._active_tasks: set[int] = set()
        self._executor = ThreadPoolExecutor(max_workers=self.MAX_CONCURRENT_TASKS)
        self._loop = None

    async def create_task(self) -> int:
        async with AsyncSessionLocal() as session:
            repo = TaskRepository(session)
            task = await repo.save_task()
            self._queue.enqueue(task.id)
            logger.info(f"Task {task.id} created and added to queue")
            return task.id
        
    async def get_task_status(self, task_id: int) -> Task:
        async with AsyncSessionLocal() as session:
            repo = TaskRepository(session)
            task = await repo.get_task(task_id, refresh=True)
            return task
        

    async def start_task_executor(self):
        self._loop = asyncio.get_event_loop()
        logger.info("Task executor started")
        
        while True:
            try:
                if len(self._active_tasks) < self.MAX_CONCURRENT_TASKS and not self._queue.is_empty():
                    task_id = self._queue.dequeue()
                    logger.info(f"Dequeued task {task_id}, active tasks: {len(self._active_tasks)}")
                    
                    async with AsyncSessionLocal() as session:
                        repo = TaskRepository(session)
                        try:
                            task = await repo.get_task(task_id)
                            task.mark_as_running()
                            await repo.update_task(task)
                            logger.info(f"Task {task_id} marked as RUNNING")
                        except Exception as e:
                            logger.error(f"Error marking task {task_id} as running: {e}")
                            continue
                    
                    self._active_tasks.add(task_id)
                    self._executor.submit(self._execute_task_sync, task_id)
                
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in task executor: {e}", exc_info=True)
                await asyncio.sleep(1)


    def _execute_task_sync(self, task_id: int):
        try:
            task_duration = random.randint(0, 10)
            logger.info(f"Task {task_id} started, will take {task_duration} seconds")
            time.sleep(task_duration)
            logger.info(f"Task {task_id} execution completed ({task_duration}s)")
            
            future = asyncio.run_coroutine_threadsafe(
                self._update_completed_task(task_id, float(task_duration)),
                self._loop
            )
            future.result(timeout=5)
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}", exc_info=True)
        finally:
            self._active_tasks.discard(task_id)
            logger.info(f"Task {task_id} removed from active tasks. Active: {len(self._active_tasks)}")


    async def _update_completed_task(self, task_id: int, exec_time: float) -> None:
        try:
            async with AsyncSessionLocal() as session:
                repo = TaskRepository(session)
                task = await repo.get_task(task_id)
                task.mark_as_completed(exec_time=exec_time)
                await repo.update_task(task)
                logger.info(f"Task {task_id} marked as COMPLETED (exec_time={exec_time}s)")
        except Exception as e:
            logger.error(f"Error updating task {task_id} to completed: {e}", exc_info=True)