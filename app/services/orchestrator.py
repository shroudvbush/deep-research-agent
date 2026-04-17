import asyncio
from app.core.llm_client import LLMClient
from app.services.planning_service import PlanningService
from app.services.search_service import SearchService
from app.services.summarization_service import SummarizationService
from app.services.reporting_service import ReportingService
from app import db


class Orchestrator:
    def __init__(self):
        self.llm = LLMClient()
        self.planning = PlanningService(self.llm)
        self.search = SearchService()
        self.summarization = SummarizationService(self.llm)
        self.reporting = ReportingService(self.llm)

    async def run_research(
        self,
        topic: str,
        constraints: str = "",
        max_tasks: int = 5,
        language: str = "zh-CN",
    ):
        all_sources: list[str] = []
        task_summaries: list = []

        try:
            yield {"event": "research_started", "message": f"Research started: {topic}", "payload": {}}

            yield {"event": "planning_started", "message": "Planning tasks...", "payload": {}}
            tasks = await self.planning.create_tasks(topic, constraints, max_tasks)
            yield {
                "event": "planning_completed",
                "message": f"Planned {len(tasks)} tasks",
                "payload": {"tasks": [t.model_dump() for t in tasks]},
            }

            for task in tasks:
                try:
                    yield {
                        "event": "task_started",
                        "message": f"Starting: {task.title}",
                        "payload": {"task_id": task.id},
                    }

                    docs = await self.search.search(f"{task.title} {task.goal}", top_k=6)
                    urls = [d.url for d in docs if d.url and d.source != "fallback"]
                    all_sources.extend(urls)

                    try:
                        task_report = {
                            "title": f"Task: {task.title}",
                            "abstract": task.goal,
                            "sections": [f"Goal: {task.goal}"],
                            "references": urls,
                        }
                        rid = db.save_record(
                            topic=f"Task: {task.title}",
                            constraints=f"Subtask of: {topic}",
                            sources=urls,
                            tasks=[t.model_dump() for t in tasks],
                            report=task_report,
                            category="research",
                        )
                        yield {
                            "event": "task_saved",
                            "message": f"Task saved: {task.title}",
                            "payload": {"id": rid, "task_id": task.id, "category": "research"},
                        }
                    except Exception as se:
                        print(f"[Orchestrator] save task record failed: {se}")

                    if not urls:
                        yield {
                            "event": "task_completed",
                            "message": f"Done: {task.title}",
                            "payload": {"task_id": task.id, "sources": []},
                        }
                    else:
                        yield {
                            "event": "task_completed",
                            "message": f"Done: {task.title} ({len(urls)} sources)",
                            "payload": {"task_id": task.id, "sources": urls},
                        }

                    summary = await self.summarization.summarize(task, docs)
                    task_summaries.append(summary)

                except Exception as e:
                    print(f"[Orchestrator] Task {task.id} error: {e}")
                    yield {
                        "event": "task_failed",
                        "message": f"Failed: {task.title} ({e})",
                        "payload": {"task_id": task.id, "error": str(e)},
                    }
                    task_summaries.append(None)

            yield {"event": "report_started", "message": "Generating report...", "payload": {}}
            report = await self.reporting.generate(topic, task_summaries, language)
            yield {
                "event": "report_completed",
                "message": "Report generated",
                "payload": {"report": report.model_dump()},
            }

            yield {"event": "research_finished", "message": "Research complete", "payload": {}}

        except Exception as e:
            print(f"[Orchestrator] Fatal error: {e}")
            yield {
                "event": "error",
                "message": str(e),
                "payload": {"stage": "orchestrator", "detail": str(e)},
            }
