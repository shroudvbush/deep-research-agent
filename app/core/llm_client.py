import httpx
from typing import Optional
from app.core.config import settings


class LLMClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or settings.LLM_BASE_URL
        self.model = model or settings.LLM_MODEL

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        return await self._post(prompt, temperature, max_tokens)

    async def acall(self, prompt: str, _history=None, _mode: str = "text") -> str:
        return await self._post(prompt, temperature=0.3, max_tokens=4096)

    async def _post(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not self.api_key:
            print("[LLMClient] WARNING: LLM_API_KEY not set, DEMO mode")
            return self._fallback_response(prompt)

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(180.0, connect=10.0),
            follow_redirects=True,
        ) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            if response.status_code != 200:
                print(f"[LLMClient] API error {response.status_code}: {response.text[:300]}")
                raise Exception(f"LLM API error: {response.status_code} — {response.text[:200]}")
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _fallback_response(self, prompt: str) -> str:
        return (
            '['
            '{"id":"task-1","title":"Definition & Scope","goal":"Define and clarify research boundaries","priority":1},'
            '{"id":"task-2","title":"Key Data & Current State","goal":"Collect current data, facts and evidence","priority":2},'
            '{"id":"task-3","title":"Comparison & Conclusion","goal":"Compare options and form recommendations","priority":3}'
            ']'
        )
