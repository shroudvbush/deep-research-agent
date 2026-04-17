from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.research import router as research_router

app = FastAPI(title="Deep Research Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research_router, prefix="/api", tags=["research"])


@app.get("/")
async def root():
    return {"message": "Deep Research Agent API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}
