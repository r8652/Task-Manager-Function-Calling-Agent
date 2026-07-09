from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional
from uuid import uuid4

Status = Literal["pending", "in_progress", "completed"]
TaskType = Literal["work", "personal", "study", "errand"]


@dataclass
class Task:
    id: str
    code: str
    title: str
    description: str = ""
    task_type: TaskType = "personal"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Status = "pending"


_tasks: list[Task] = []


def _generate_code() -> str:
    return f"TASK-{uuid4().hex[:8].upper()}"


def _serialize_task(task: Task) -> dict[str, object]:
    return {
        "id": task.id,
        "code": task.code,
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "start_date": task.start_date,
        "end_date": task.end_date,
        "status": task.status,
    }


def get_tasks(
    status: Optional[Status] = None,
    task_type: Optional[TaskType] = None,
    code: Optional[str] = None,
) -> list[dict[str, object]]:
    tasks = list(_tasks)
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if task_type is not None:
        tasks = [task for task in tasks if task.task_type == task_type]
    if code is not None:
        tasks = [task for task in tasks if task.code == code]
    return [_serialize_task(task) for task in tasks]


def add_task(
    title: str,
    description: str = "",
    task_type: TaskType = "personal",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Status = "pending",
    code: Optional[str] = None,
) -> dict[str, object]:
    task = Task(
        id=str(uuid4()),
        code=code or _generate_code(),
        title=title,
        description=description,
        task_type=task_type,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )
    _tasks.append(task)
    return _serialize_task(task)


def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    task_type: Optional[TaskType] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[Status] = None,
    code: Optional[str] = None,
) -> Optional[dict[str, object]]:
    for task in _tasks:
        if task.id == task_id:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if task_type is not None:
                task.task_type = task_type
            if start_date is not None:
                task.start_date = start_date
            if end_date is not None:
                task.end_date = end_date
            if status is not None:
                task.status = status
            if code is not None:
                task.code = code
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
