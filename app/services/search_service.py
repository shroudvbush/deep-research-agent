from typing import List
from dataclasses import dataclass
from app.core.config import settings
import httpx
import json as _json


@dataclass
class SearchResult:
    title: str
    snippet: str
    url: str
    source: str


class SearchService:
    def __init__(self):
        self.provider = settings.SEARCH_PROVIDER

    async def search(self, query: str, top_k: int = 6) -> List[SearchResult]:
        query = query.strip()
        if not query:
            return []

        print(f"[SearchService] provider={self.provider} query={query!r}")
        try:
            results = await self._search_deepseek_llm(query, top_k)
            real_count = sum(1 for r in results if r.url and r.source != "fallback")
            print(f"[SearchService] results={len(results)} real_urls={real_count}")
            return results
        except Exception as e:
            print(f"[SearchService] Search failed ({type(e).__name__}): {e}")
            return self._fallback_results(query)

    async def _search_deepseek_llm(self, query: str, top_k: int) -> List[SearchResult]:
        from app.core.llm_client import LLMClient

        llm = LLMClient()
        prompt = (
            f"You are a research assistant. Provide {top_k} most valuable reference sources for the following topic. "
            f"For each, provide: title, a short snippet (under 100 chars), and a real accessible URL.\n\n"
            f"Topic: {query}\n\n"
            f"Return only a JSON array, no additional text:\n"
            f'[{{"title":"Title","snippet":"Snippet (under 100 chars)","url":"https://example.com"}}]'
        )

        resp_text = await llm.acall(prompt, [], "json")
        print(f"[SearchService] DeepSeek raw response: {resp_text[:200]}")

        try:
            items = _json.loads(resp_text)
            results = []
            seen = set()
            for item in (items if isinstance(items, list) else [])[:top_k]:
                url = (item.get("url") or "").strip()
                title = (item.get("title") or "").strip()
                snippet = (item.get("snippet") or "")[:300]
                if title and url and "example" not in url and url not in seen:
                    seen.add(url)
                    results.append(SearchResult(title=title, snippet=snippet, url=url, source="deepseek"))
            return results
        except Exception as e:
            print(f"[SearchService] JSON parse failed: {e}, raw: {resp_text[:300]}")
            return []

    def _fallback_results(self, query: str) -> List[SearchResult]:
        return [
            SearchResult(
                title=f"Reference for: {query}",
                snippet="Search service unavailable. Please configure a valid search API.",
                url="",
                source="fallback",
            )
        ]
