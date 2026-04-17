from typing import List
from app.models.report import ResearchReport
from app.models.research_task import TaskExecutionResult


class ReportingService:
    def __init__(self, llm_client):
        self.llm = llm_client

    async def generate(
        self, topic: str, task_results: List[TaskExecutionResult], language: str = "zh-CN"
    ) -> ResearchReport:
        results_text = "\n\n".join(
            f"## Task: {r.task_id}\nSummary: {r.summary}\nKey Findings:"
            + "\n".join(f"- {f}" for f in r.key_findings)
            + "\nSources:"
            + "\n".join(f"- {s}" for s in r.sources)
            for r in task_results
        )

        lang_instruction = "Respond in Simplified Chinese" if language.startswith("zh") else "Respond in English"

        prompt = f"""{lang_instruction}. You are a professional research report writer. Based on the following task results, write a complete research report.

## Research Topic
{topic}

## Task Results
{results_text}

Output strict JSON format (no additional text):
{{
  "title": "Report Title",
  "abstract": "Executive Summary (under 150 chars)",
  "sections": ["Section Title||Section Content", "Section Title||Section Content", ...],
  "references": ["Source 1", "Source 2", ...]
}}

Suggested structure: 1. Executive Summary 2. Background 3. Key Findings 4. Analysis & Recommendations 5. Risks & Limitations 6. References
"""

        raw = await self.llm.generate(prompt, max_tokens=4096)
        try:
            import re, json

            m = re.search(r"\{.*\}", raw, flags=re.S)
            if m:
                data = json.loads(m.group(0))
                return ResearchReport(
                    title=data.get("title", f"{topic} Research Report"),
                    abstract=data.get("abstract", ""),
                    sections=data.get("sections", []),
                    references=data.get("references", []),
                )
        except Exception:
            pass

        sections = []
        references = []
        for r in task_results:
            sections.append(
                f"{r.task_id}||{r.summary}\n" + "\n".join(f"- {f}" for f in r.key_findings)
            )
            references.extend(r.sources)

        return ResearchReport(
            title=f"{topic} Research Report",
            abstract=f"This report covers {topic} with {len(task_results)} research dimensions.",
            sections=sections,
            references=list(dict.fromkeys(references)),
        )
