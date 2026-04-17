import json
import re
from typing import List
from app.models.research_task import ResearchTask


class PlanningService:
    def __init__(self, llm_client):
        self.llm = llm_client

    async def create_tasks(
        self, topic: str, constraints: str, max_tasks: int
    ) -> List[ResearchTask]:
        prompt = f"""You are a research planning assistant. Break down the following research topic into {max_tasks} specific, actionable tasks.
Topic: {topic}
Constraints: {constraints or 'None'}
Output a strict JSON array with fields: id, title, goal, priority (1=highest, 5=lowest).
Output JSON only, no additional text."""

        raw = await self.llm.generate(prompt)
        tasks = self._extract_tasks(raw)
        if not tasks:
            tasks = self._fallback_tasks(topic)
        return tasks[:max_tasks]

    def _extract_tasks(self, text: str) -> List[ResearchTask]:
        try:
            m = re.search(r"\[.*\]", text, flags=re.S)
            if not m:
                return []
            arr = json.loads(m.group(0))
            result = []
            for i, item in enumerate(arr):
                result.append(
                    ResearchTask(
                        id=str(item.get("id", f"task-{i+1}")),
                        title=item["title"],
                        goal=item["goal"],
                        priority=int(item.get("priority", 3)),
                    )
                )
            return result
        except Exception:
            return []

    def _fallback_tasks(self, topic: str) -> List[ResearchTask]:
        return [
            ResearchTask(id="task-1", title="Definition & Scope",
                         goal=f"Define {topic} and clarify research boundaries", priority=1),
            ResearchTask(id="task-2", title="Key Data & Current State",
                         goal=f"Collect current data, facts and evidence on {topic}", priority=2),
            ResearchTask(id="task-3", title="Comparison & Conclusion",
                         goal=f"Compare options and form recommendations on {topic}", priority=3),
        ]
