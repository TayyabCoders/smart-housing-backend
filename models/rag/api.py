"""
O.T.T.O RAG API — FastAPI service consumed by the main backend's
/api/v1/chatbot route (see smart-housing-backend/app/services/chatbot_service.py).

Run:
    uvicorn api:app --host 0.0.0.0 --port 8001 --reload
"""
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.otto_engine import ask, get_all_collections

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("otto-api")

app = FastAPI(title="O.T.T.O RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    collections: list[str] | None = None


class ChatResponse(BaseModel):
    answer: str
    collections_used: list[str]


@app.get("/health")
def health():
    return {"status": "ok", "collections": get_all_collections()}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        return ask(req.query.strip(), req.collections)
    except Exception:
        logger.exception("OTTO chat failed")
        raise HTTPException(status_code=502, detail="O.T.T.O failed to generate a response")
