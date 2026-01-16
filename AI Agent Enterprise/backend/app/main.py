from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .rag import answer_question, answer_question_with_employee

app = FastAPI(title="RAG Knowledge Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str
    employee_id: str | None = None
    llm_provider: str = Field(default="none", description="openai | gemini | none")
    llm_model: str = Field(default="gpt-4o-mini")
    top_k: int = Field(default=4, ge=1, le=10)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    if req.employee_id:
        result = answer_question_with_employee(
            req.question,
            req.employee_id,
            req.llm_provider,
            req.llm_model,
            top_k=req.top_k,
        )
    else:
        result = answer_question(
            req.question,
            req.llm_provider,
            req.llm_model,
            top_k=req.top_k,
        )
    return result
