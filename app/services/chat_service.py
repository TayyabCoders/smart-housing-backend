from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status

from app.schemas.chat_schema import MessageCreate, MessageResponse, ConversationResponse
from app.di.container import container
import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class ChatService:
    @inject
    def __init__(
        self,
        message_repository = Provide["message_repository"],
        conversation_repository = Provide["conversation_repository"],
        user_repository = Provide["user_repository"],
        prometheus = Provide["prometheus"],
    ):
        self.message_repository = message_repository
        self.conversation_repository = conversation_repository
        self.user_repository = user_repository
        self.prometheus = prometheus
    
    async def send_message(self, sender_id: UUID, message_data: MessageCreate) -> MessageResponse:
        """Send a message to another user"""
        try:
            logger.info(f"ChatService: Sending message from {sender_id} to {message_data.receiver_id}")
            
            # Verify receiver exists
            receiver = await self.user_repository.findById(message_data.receiver_id)
            if not receiver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Receiver not found"
                )
            
            # Create message
            message_dict = {
                "sender_id": sender_id,
                "receiver_id": message_data.receiver_id,
                "content": message_data.content,
                "is_read": False
            }
            message = await self.message_repository.create(message_dict)
            
            # Update or create conversation
            conversation = await self.conversation_repository.findConversation(
                sender_id, message_data.receiver_id
            )
            
            if conversation:
                # Update existing conversation
                await self.conversation_repository.update(
                    conversation.id,
                    {
                        "last_message": message_data.content,
                        "last_message_time": datetime.utcnow()
                    }
                )
                
                # Increment unread count for receiver
                if conversation.user1_id == message_data.receiver_id:
                    await self.conversation_repository.updateUnreadCount(
                        conversation.id, message_data.receiver_id, conversation.unread_count_user1 + 1
                    )
                else:
                    await self.conversation_repository.updateUnreadCount(
                        conversation.id, message_data.receiver_id, conversation.unread_count_user2 + 1
                    )
            else:
                # Create new conversation
                conversation_dict = {
                    "user1_id": sender_id,
                    "user2_id": message_data.receiver_id,
                    "last_message": message_data.content,
                    "last_message_time": datetime.utcnow(),
                    "unread_count_user1": 0,
                    "unread_count_user2": 1
                }
                await self.conversation_repository.create(conversation_dict)
            
            logger.info(f"ChatService: Message sent successfully")
            
            # Record business event
            self.prometheus.record_business_event("message_sent", "success")
            
            # Send real-time notification via WebSocket if receiver is online
            from app.edge.socket.connection_manager import manager
            # WebSocket connections use email as user_id (from JWT sub claim)
            await manager.send_to_user({
                "type": "chat_message",
                "data": {
                    "id": str(message.id),
                    "sender_id": str(sender_id),
                    "receiver_id": str(message_data.receiver_id),
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                    "is_read": message.is_read
                }
            }, receiver.email)
            
            return MessageResponse.model_validate(message)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("ChatService: Failed to send message.", exc_info=True)
            raise e

    async def get_conversations(self, user_id: UUID) -> List[ConversationResponse]:
        """Get all conversations for a user"""
        try:
            logger.info(f"ChatService: Getting conversations for user {user_id}")
            
            conversations = await self.conversation_repository.findUserConversations(user_id)
            
            result = []
            for conv in conversations:
                # Determine the other user
                other_user_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
                other_user = await self.user_repository.findById(other_user_id)
                
                if not other_user:
                    continue
                
                # Get unread count for current user
                unread_count = conv.unread_count_user2 if conv.user1_id == user_id else conv.unread_count_user1
                
                # Check if user is online using existing connection manager
                from app.edge.socket.connection_manager import manager
                is_online = str(other_user_id) in manager.user_connections
                
                result.append(ConversationResponse(
                    id=conv.id,
                    user_id=other_user.id,
                    username=other_user.username,
                    last_message=conv.last_message,
                    last_message_time=conv.last_message_time,
                    unread_count=unread_count,
                    is_online=is_online
                ))
            
            logger.info(f"ChatService: Retrieved {len(result)} conversations")
            
            return result
        
        except Exception as e:
            logger.error("ChatService: Failed to get conversations.", exc_info=True)
            raise e

    async def get_messages(self, user_id: UUID, other_user_id: UUID, limit: int = 50, offset: int = 0) -> List[MessageResponse]:
        """Get message history between two users"""
        try:
            logger.info(f"ChatService: Getting messages between {user_id} and {other_user_id}")
            
            messages = await self.message_repository.findConversationMessages(
                user_id, other_user_id, limit, offset
            )
            
            # Mark messages as read
            await self.message_repository.markAsRead(other_user_id, user_id)
            
            # Update conversation unread count
            conversation = await self.conversation_repository.findConversation(user_id, other_user_id)
            if conversation:
                await self.conversation_repository.updateUnreadCount(conversation.id, user_id, 0)
            
            # Reverse to show oldest first
            messages_reversed = list(reversed(messages))
            
            logger.info(f"ChatService: Retrieved {len(messages_reversed)} messages")
            
            return [MessageResponse.model_validate(msg) for msg in messages_reversed]
        
        except Exception as e:
            logger.error("ChatService: Failed to get messages.", exc_info=True)
            raise e

    async def mark_message_read(self, message_id: UUID, user_id: UUID) -> Dict[str, str]:
        """Mark a specific message as read"""
        try:
            logger.info(f"ChatService: Marking message {message_id} as read")
            
            # Find the message
            message = await self.message_repository.findById(message_id)
            if not message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Message not found"
                )
            
            # Verify user is the receiver
            if message.receiver_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only mark your own messages as read"
                )
            
            # Update message
            await self.message_repository.update(message_id, {"is_read": True})
            
            logger.info("ChatService: Message marked as read successfully")
            
            return {"status": "success"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("ChatService: Failed to mark message as read.", exc_info=True)
            raise e
