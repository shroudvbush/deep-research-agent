from pydantic import BaseModel
from typing import Literal, List

TaskStatus = Literal["pending", "running", "completed", "failed"]


class ResearchTask(BaseModel):
    id: str
    title: str
    goal: str
    status: TaskStatus = "pending"
    priority: int = 3


class TaskExecutionResult(BaseModel):
    task_id: str
    summary: str
    key_findings: List[str]
    sources: List[str]
