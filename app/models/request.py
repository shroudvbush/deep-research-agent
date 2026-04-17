from pydantic import BaseModel, Field
from typing import Optional


class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Research topic")
    constraints: Optional[str] = Field(default="", description="Additional constraints")
    language: str = Field(default="zh-CN", description="Output language")
    max_tasks: int = Field(default=5, ge=3, le=10, description="Maximum number of tasks")
