from typing import List

class TaskAgent:
    def __init__(self, memory_manager=None):
        self.queue: List[str] = []
        self.memory = memory_manager

    def add_task(self, task_description: str):
        self.queue.append(task_description)

    def execute_next_task(self):
        if not self.queue:
            return None
        task = self.queue.pop(0)
        # simple simulation of task processing
        result = f"Executed: {task}"
        print(result)
        if self.memory:
            # store the result using task as key
            self.memory.store_memory(task, result)
        return result
