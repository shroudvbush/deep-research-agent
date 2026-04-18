from typing import List
from dataclasses import dataclass
from app.core.config import settings
import httpx


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
            if self.provider == "tavily" and settings.TAVILY_API_KEY:
                return await self._search_tavily(query, top_k)
            else:
                return await self._search_duckduckgo(query, top_k)
        except Exception as e:
            print(f"[SearchService] Search failed ({type(e).__name__}): {e}")
            return self._fallback_results(query)

    async def _search_tavily(self, query: str, top_k: int) -> List[SearchResult]:
        """Tavily API 搜索（需要 API Key）"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={"query": query, "api_key": settings.TAVILY_API_KEY, "max_results": top_k},
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            seen_urls = set()
            for item in data.get("results", []):
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    results.append(
                        SearchResult(
                            title=item.get("title", ""),
                            snippet=item.get("content", "")[:300],
                            url=url,
                            source="tavily",
                        )
                    )
            print(f"[SearchService] Tavily results={len(results)}")
            return results[:top_k]

    async def _search_duckduckgo(self, query: str, top_k: int) -> List[SearchResult]:
        """DuckDuckGo 搜索（免费，无需 API Key）"""
        try:
            from duckduckgo_search import AsyncDDGS

            ddgs = AsyncDDGS()
            results = []
            seen_urls = set()
            async for r in ddgs.atext(query, max_results=top_k * 2):
                title = r.get("title", "")[:80]
                snippet = r.get("body", "")[:300]
                url = r.get("href", "")
                if title and url and url not in seen_urls:
                    seen_urls.add(url)
                    results.append(
                        SearchResult(
                            title=title,
                            snippet=snippet,
                            url=url,
                            source="duckduckgo",
                        )
                    )
                if len(results) >= top_k:
                    break
            print(f"[SearchService] DuckDuckGo results={len(results)}")
            return results
        except ImportError:
            print("[SearchService] duckduckgo-search not installed, using fallback")
            return self._fallback_results(query)
        except Exception as e:
            print(f"[SearchService] DuckDuckGo error: {e}")
            return self._fallback_results(query)

    def _fallback_results(self, query: str) -> List[SearchResult]:
        """当搜索不可用时的占位结果"""
        return [
            SearchResult(
                title=f"关于「{query}」的参考资料",
                snippet="搜索服务暂不可用。请安装 duckduckgo-search（pip install duckduckgo-search）或配置 Tavily API Key。",
                url="",
                source="fallback",
            )
        ]
