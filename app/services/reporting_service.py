from typing import List
from app.models.report import ResearchReport
from app.models.research_task import TaskExecutionResult


class ReportingService:
    def __init__(self, llm_client):
        self.llm = llm_client

    async def generate(
        self, topic: str, task_results: List[TaskExecutionResult], language: str = "zh-CN"
    ) -> ResearchReport:
        # Filter out failed tasks
        valid_results = [r for r in task_results if r and r.summary]
        if not valid_results:
            return ResearchReport(
                title=f"{topic} 研究报告",
                abstract="本研究未能获取有效研究结果。",
                sections=[f"{topic}||暂无内容"],
                references=[],
            )

        results_text = "\n\n".join(
            f"## 子任务：{r.task_id}\n"
            f"**摘要**：{r.summary}\n\n"
            f"**关键发现**：\n" + "\n".join(f"- {f}" for f in r.key_findings)
            + "\n\n**参考来源**：\n" + "\n".join(f"- {s}" for s in r.sources)
            for r in valid_results
        )

        if language.startswith("zh"):
            prompt = f"""你是一位资深研究报告撰写专家。请基于以下研究结果，撰写一份专业、深入的研究报告。

## 研究主题
{topic}

## 研究结果汇总
{results_text}

## 输出要求

请严格按以下 JSON 格式输出（不要有其他文字）：

{{
  "title": "报告标题（简洁有力，体现研究核心）",
  "abstract": "执行摘要（200-300字，概括研究目的、方法、主要发现和结论）",
  "sections": [
    "一、研究背景与问题提出||阐述研究主题的背景、意义及核心问题...",
    "二、文献综述||梳理相关领域的研究现状与理论基础...",
    "三、核心发现与分析||详细呈现各子任务的研究成果...",
    "四、讨论与建议||对研究发现进行深入讨论并提出建设性建议...",
    "五、结论与展望||总结研究结论，指出研究局限与未来方向..."
  ],
  "references": [
    "作者. 标题. 来源. 年份",
    ...
  ]
}}

## 注意事项

1. 报告应体现学术规范性，结构清晰，逻辑严密
2. 各章节内容应详实具体，避免空泛陈述
3. 关键论点需有数据或事实支撑
4. 参考文献应按学术规范格式列出，至少包含5条高质量来源
5. 语言应专业、客观，避免主观臆断
"""
        else:
            prompt = f"""You are a senior research report writer. Based on the following research results, write a professional and in-depth research report.

## Research Topic
{topic}

## Research Results
{results_text}

## Output Requirements

Output strictly in JSON format (no additional text):

{{
  "title": "Report Title (concise and impactful)",
  "abstract": "Executive Summary (200-300 words, covering purpose, methods, findings and conclusions)",
  "sections": [
    "1. Introduction and Background||Describe the background and significance...",
    "2. Literature Review||Summarize related research...",
    "3. Key Findings and Analysis||Present research results in detail...",
    "4. Discussion and Recommendations||Discuss findings and provide suggestions...",
    "5. Conclusions and Future Work||Summarize conclusions and limitations..."
  ],
  "references": [
    "Author. Title. Source. Year",
    ...
  ]
}}

## Notes

1. Report should be academically rigorous with clear structure
2. Content should be substantial, avoid vague statements
3. Key arguments should be supported by data or facts
4. References should follow academic format, at least 5 high-quality sources
5. Language should be professional and objective
"""

        raw = await self.llm.generate(prompt, max_tokens=4096)
        try:
            import re, json

            m = re.search(r"\{.*\}", raw, flags=re.S)
            if m:
                data = json.loads(m.group(0))
                return ResearchReport(
                    title=data.get("title", f"{topic} 研究报告"),
                    abstract=data.get("abstract", ""),
                    sections=data.get("sections", []),
                    references=data.get("references", []),
                )
        except Exception as e:
            print(f"[ReportingService] JSON parse failed: {e}")

        # Fallback: 直接用研究结果构建报告
        sections = []
        references = []
        for r in valid_results:
            findings_text = "\n".join(f"- {f}" for f in r.key_findings)
            sections.append(f"{r.task_id}||{r.summary}\n\n{findings_text}")
            references.extend(r.sources)

        return ResearchReport(
            title=f"{topic} 研究报告",
            abstract=f"本报告围绕「{topic}」展开研究，涵盖 {len(valid_results)} 个核心维度。",
            sections=sections,
            references=list(dict.fromkeys(references)),
        )
