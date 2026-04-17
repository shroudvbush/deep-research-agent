import json
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.services.orchestrator import Orchestrator
from app import db

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/research/stream")
async def research_stream(
    topic: str = Body(...),
    constraints: str = Body(""),
    max_tasks: int = Body(5),
    language: str = Body("zh-CN"),
    category: str = Body("research"),
):
    async def gen():
        sources, tasks, report_data = [], [], {}

        try:
            async for event in orchestrator.run_research(topic, constraints, max_tasks, language):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                ev_data = event.get("payload") or {}
                if event["event"] == "planning_completed":
                    tasks = ev_data.get("tasks", [])
                elif event["event"] == "task_completed":
                    sources.extend(ev_data.get("sources", []))
                elif event["event"] == "report_completed":
                    report_data = ev_data.get("report", {})

        except Exception as e:
            yield f"data: {json.dumps({'event':'error','message':str(e),'payload':{'stage':'orchestrator','detail':str(e)}}, ensure_ascii=False)}\n\n"
            report_data = {"title": "Research Failed", "abstract": str(e), "sections": [], "references": []}

        try:
            rid = db.save_record(
                topic=topic,
                constraints=constraints,
                sources=list(set(sources)),
                tasks=tasks,
                report=report_data,
                category=category,
            )
            yield f"data: {json.dumps({'event':'history_saved','message':'Saved','payload':{'id':rid}}, ensure_ascii=False)}\n\n"
        except Exception as e:
            print(f"[research] save history failed: {e}")

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


class HistorySavePayload(BaseModel):
    topic: str
    constraints: str = ""
    category: str = "research"
    sources: list = []
    tasks: list = []
    report: dict = {}


@router.post("/research/history")
def save_history(body: HistorySavePayload):
    rid = db.save_record(
        topic=body.topic,
        constraints=body.constraints,
        sources=body.sources,
        tasks=body.tasks,
        report=body.report,
        category=body.category,
    )
    return {"id": rid, "message": "Saved"}


@router.get("/research/history")
def list_history(category: Optional[str] = None, limit: int = 50):
    rows = db.get_all_history(category or "", limit)
    for r in rows:
        r["sources"] = json.loads(r.get("sources", "[]"))
        r["tasks"] = json.loads(r.get("tasks", "[]"))
        r["report"] = json.loads(r.get("report", "{}"))
    return rows


@router.get("/research/history/{rid}")
def get_history(rid: int):
    row = db.get_record(rid)
    if not row:
        return {"error": "Not found"}
    row["sources"] = json.loads(row.get("sources", "[]"))
    row["tasks"] = json.loads(row.get("tasks", "[]"))
    row["report"] = json.loads(row.get("report", "{}"))
    return row


@router.delete("/research/history/{rid}")
def delete_history(rid: int):
    ok = db.delete_record(rid)
    return {"deleted": ok, "message": "Deleted" if ok else "Not found"}
