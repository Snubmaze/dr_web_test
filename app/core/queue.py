from threading import Lock


class Queue:
    def __init__(self):
        self._lock = Lock()
        self._items: list[int] = []

    def enqueue(self, task_id: int) -> None:
        with self._lock:
            self._items.append(task_id)

    def dequeue(self) -> int:
        with self._lock:
            if not len(self._items):
                raise IndexError("Queue is empty")
            return self._items.pop(0)

    def is_empty(self) -> bool:
        with self._lock:
            return len(self._items) == 0
    
    def get_size(self) -> int:
        with self._lock:
            return len(self._items)