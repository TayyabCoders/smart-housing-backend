"""
Chat endpoints
"""
from fastapi import APIRouter, Depends, Query
from app.schemas.chat_schema import MessageCreate, MessageResponse, ConversationResponse
from app.edge.http.controller.chat_controller import ChatController
from app.di.container import container
from dependency_injector.wiring import inject, Provide
from app.middlewares.auth_middleware import get_current_user
from app.models.user_model import User
from uuid import UUID

router = APIRouter()


@router.post("/messages", response_model=MessageResponse)
@inject
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    chat_controller: ChatController = Depends(Provide["chat_controller"])
):
    """Send a message to another user"""
    return await chat_controller.send_message(current_user.id, message_data)


@router.get("/conversations", response_model=list[ConversationResponse])
@inject
async def get_conversations(
    current_user: User = Depends(get_current_user),
    chat_controller: ChatController = Depends(Provide["chat_controller"])
):
    """Get all conversations for the current user"""
    return await chat_controller.get_conversations(current_user.id)


@router.get("/messages/{user_id}", response_model=list[MessageResponse])
@inject
async def get_messages(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    chat_controller: ChatController = Depends(Provide["chat_controller"])
):
    """Get message history between current user and another user"""
    return await chat_controller.get_messages(current_user.id, user_id, limit, offset)


@router.put("/messages/{message_id}/read")
@inject
async def mark_message_read(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    chat_controller: ChatController = Depends(Provide["chat_controller"])
):
    """Mark a specific message as read"""
    return await chat_controller.mark_message_read(message_id, current_user.id)
