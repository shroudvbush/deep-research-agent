import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "duckduckgo")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")


settings = Settings()
