"""
Chatbot (O.T.T.O) Schema
"""
from pydantic import BaseModel, Field


class ChatbotAskRequest(BaseModel):
    query: str = Field(min_length=1)


class ChatbotAskResponse(BaseModel):
    answer: str
    collections_used: list[str]
