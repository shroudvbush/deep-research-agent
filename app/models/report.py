from pydantic import BaseModel
from typing import List


class ResearchReport(BaseModel):
    title: str
    abstract: str
    sections: List[str]
    references: List[str]
