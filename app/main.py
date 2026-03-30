from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.rag_pipeline import RagPipeline

app = FastAPI(title="Enterprise RAG API", version="1.0.0")
pipeline = RagPipeline()


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    return pipeline.ask(req.question)
