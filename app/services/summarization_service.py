from typing import List
from app.models.research_task import ResearchTask, TaskExecutionResult
from app.services.search_service import SearchResult


class SummarizationService:
    def __init__(self, llm_client):
        self.llm = llm_client

    async def summarize(
        self, task: ResearchTask, docs: List[SearchResult]
    ) -> TaskExecutionResult:
        real_docs = [d for d in docs if d.url and d.source != "fallback"]
        print(
            f"[SummarizationService] task={task.id} docs_total={len(docs)} real_urls={len(real_docs)}"
        )

        if not real_docs:
            return TaskExecutionResult(
                task_id=task.id,
                summary=(
                    f"No valid search results for \"{task.title}\". "
                    "Please check: ① pip install duckduckgo-search ② SEARCH_PROVIDER / API Key settings."
                ),
                key_findings=[],
                sources=[],
            )

        docs_text = "\n\n".join(
            f"- [{d.title}]({d.url})\n  {d.snippet}" for d in real_docs
        )

        prompt = f"""You are a research summarization assistant. Based on the following search results, provide a deep summary of this research task.

## Task
Title: {task.title}
Goal: {task.goal}

## Search Results
{docs_text}

Output strict JSON format (no additional text):
{{"summary":"Summary (under 100 chars)","key_findings":["Finding 1","Finding 2","Finding 3"],"sources":["Title: URL","..."]}}
"""

        raw = await self.llm.generate(prompt, max_tokens=1024)
        try:
            import re, json

            m = re.search(r"\{.*\}", raw, flags=re.S)
            if m:
                data = json.loads(m.group(0))
                return TaskExecutionResult(
                    task_id=task.id,
                    summary=data.get("summary", ""),
                    key_findings=data.get("key_findings", []),
                    sources=data.get("sources", [d.url for d in real_docs]),
                )
        except Exception as e:
            print(f"[SummarizationService] JSON parse failed: {e}")

        return TaskExecutionResult(
            task_id=task.id,
            summary=f"Completed research on \"{task.title}\" based on {len(real_docs)} sources.",
            key_findings=[d.snippet[:100] for d in real_docs if d.snippet],
            sources=[d.url for d in real_docs],
        )
