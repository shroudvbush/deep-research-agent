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
                summary=f"任务「{task.title}」未获取到有效检索结果，请检查搜索配置。",
                key_findings=[],
                sources=[],
            )

        docs_text = "\n\n".join(
            f"### [{d.title}]({d.url})\n{d.snippet}" for d in real_docs
        )

        # 构建 sources 列表（在 f-string 外部，避免作用域冲突）
        sources_list = [f"{d.title}: {d.url}" for d in real_docs]

        prompt = f"""你是一位专业研究分析师。请基于以下搜索结果，对研究任务进行深度分析和总结。

## 研究任务
- **任务编号**：{task.id}
- **任务标题**：{task.title}
- **研究目标**：{task.goal}

## 搜索结果
{docs_text}

## 输出要求

请严格按以下 JSON 格式输出（不要有其他文字）：

{{
  "summary": "任务总结（150-200字，涵盖研究发现的核心观点、数据支撑和结论）",
  "key_findings": [
    "发现1：具体描述，引用来源或数据",
    "发现2：具体描述，引用来源或数据",
    "发现3：具体描述，引用来源或数据",
    "发现4：具体描述，引用来源或数据",
    "发现5：具体描述，引用来源或数据"
  ],
  "sources": [
    src for src in sources_list
  ]
}}

## 注意事项

1. 总结应体现研究深度，不能只是简单复述
2. 关键发现应有具体数据、事实或观点支撑
3. 发现数量建议在3-5条，每条控制在50字以内
4. 来源格式：标题 + URL
"""

        raw = await self.llm.generate(prompt, max_tokens=2048)
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

        # Fallback: 基于搜索结果构建基础摘要
        snippets = [d.snippet for d in real_docs if d.snippet]
        return TaskExecutionResult(
            task_id=task.id,
            summary=f"基于 {len(real_docs)} 个来源完成了「{task.title}」的研究。",
            key_findings=snippets[:5] if snippets else [],
            sources=[d.url for d in real_docs],
        )
