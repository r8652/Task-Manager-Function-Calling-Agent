from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional
from uuid import uuid4

Status = Literal["pending", "in_progress", "completed"]
TaskType = Literal["work", "personal", "study", "errand"]


@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    status: Status = "pending"
    task_type: TaskType = "personal"


_tasks: list[Task] = []


def _serialize_task(task: Task) -> dict[str, object]:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "task_type": task.task_type,
    }


def get_tasks(
    status: Optional[Status] = None,
    task_type: Optional[TaskType] = None,
) -> list[dict[str, object]]:
    tasks = list(_tasks)
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if task_type is not None:
        tasks = [task for task in tasks if task.task_type == task_type]
    return [_serialize_task(task) for task in tasks]


def add_task(
    title: str,
    description: str = "",
    status: Status = "pending",
    task_type: TaskType = "personal",
) -> dict[str, object]:
    task = Task(
        id=str(uuid4()),
        title=title,
        description=description,
        status=status,
        task_type=task_type,
    )
    _tasks.append(task)
    return _serialize_task(task)


def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[Status] = None,
    task_type: Optional[TaskType] = None,
) -> Optional[dict[str, object]]:
    for task in _tasks:
        if task.id == task_id:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.status = status
            if task_type is not None:
                task.task_type = task_type
            return _serialize_task(task)
    return None


def delete_task(task_id: str) -> dict[str, object]:
    global _tasks
    original_length = len(_tasks)
    _tasks = [task for task in _tasks if task.id != task_id]
    return {
        "deleted": len(_tasks) < original_length,
        "task_id": task_id,
    }
