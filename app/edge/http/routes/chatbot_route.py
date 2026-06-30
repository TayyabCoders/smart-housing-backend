"""
Chatbot (O.T.T.O) endpoints
"""
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.schemas.chatbot_schema import ChatbotAskRequest, ChatbotAskResponse
from app.edge.http.controller.chatbot_controller import ChatbotController
from app.middlewares.auth_middleware import get_current_user
from app.models.user_model import User

router = APIRouter()


@router.post("/ask", response_model=ChatbotAskResponse)
@inject
async def ask_chatbot(
    payload: ChatbotAskRequest,
    current_user: User = Depends(get_current_user),
    chatbot_controller: ChatbotController = Depends(Provide["chatbot_controller"])
):
    """Ask O.T.T.O a question and get a RAG-grounded answer."""
    return await chatbot_controller.ask(payload.query)
