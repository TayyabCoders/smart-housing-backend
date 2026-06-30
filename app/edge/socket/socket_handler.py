from typing import Any, Dict
import structlog
from app.edge.socket.connection_manager import manager
from app.schemas.socket_schema import SocketEvent, SocketResponse
from app.di.container import container

logger = structlog.get_logger(__name__)

class SocketHandler:
    """Handles incoming WebSocket message logic with validation"""
    
    def __init__(self):
        self._chat_mediator = None
    
    @property
    def chat_mediator(self):
        """Lazy load chat_mediator from container"""
        if self._chat_mediator is None:
            self._chat_mediator = container.resolve("chat_mediator")
        return self._chat_mediator
    
    async def handle_message(self, client_id: str, data: Dict[str, Any], user_id: str):
        """
        Process incoming message based on type
        """
        try:
            # Validate incoming data
            event = SocketEvent(**data)
            msg_type = event.type
            payload = event.payload
            
            logger.info(f"Handling '{msg_type}' message from {user_id} ({client_id})")
            
            if msg_type == "ping":
                await manager.send_personal_message({"type": "pong"}, client_id)
                
            elif msg_type == "subscribe":
                room_id = payload.get("room_id")
                if room_id:
                    await manager.join_room(client_id, room_id)
                    await manager.send_personal_message(
                        SocketResponse(type="subscribed", data={"room_id": room_id}).model_dump(),
                        client_id
                    )
                    
            elif msg_type == "unsubscribe":
                room_id = payload.get("room_id")
                if room_id:
                    await manager.leave_room(client_id, room_id)
                    await manager.send_personal_message(
                        SocketResponse(type="unsubscribed", data={"room_id": room_id}).model_dump(),
                        client_id
                    )
                    
            elif msg_type == "room_message":
                room_id = payload.get("room_id")
                content = payload.get("content")
                if room_id:
                    await manager.send_to_room({
                        "type": "room_notification",
                        "from": user_id,
                        "room_id": room_id,
                        "content": content
                    }, room_id, exclude_client=client_id)
                    
            elif msg_type == "broadcast":
                content = payload.get("content", "")
                await manager.broadcast({
                    "type": "notification",
                    "from": user_id,
                    "content": content
                })
            
            # Chat-specific message types
            elif msg_type == "chat_message":
                await self._handle_chat_message(client_id, payload, user_id)
                
            elif msg_type == "typing":
                await self._handle_typing_indicator(client_id, payload, user_id)
                
            elif msg_type == "read_receipt":
                await self._handle_read_receipt(client_id, payload, user_id)
            
            else:
                logger.warning(f"Unknown message type received: {msg_type}")
                await manager.send_personal_message(
                    SocketResponse(type="error", data={}, status="error", message="Unknown message type").model_dump(),
                    client_id
                )

        except Exception as e:
            logger.error(f"Error handling socket message: {e}")
            await manager.send_personal_message(
                SocketResponse(type="error", data={}, status="error", message=str(e)).model_dump(),
                client_id
            )
    
    async def _handle_chat_message(self, client_id: str, payload: Dict[str, Any], user_id: str):
        """Handle chat message via WebSocket"""
        try:
            from app.schemas.chat_schema import MessageCreate
            from uuid import UUID
            
            receiver_id = payload.get("receiver_id")
            content = payload.get("content")
            
            if not receiver_id or not content:
                await manager.send_personal_message(
                    SocketResponse(type="error", data={}, status="error", message="Missing receiver_id or content").model_dump(),
                    client_id
                )
                return
            
            # Create message via chat mediator
            message_data = MessageCreate(
                receiver_id=UUID(receiver_id),
                content=content
            )
            
            # Get sender user UUID from repository (user_id is email from JWT)
            from app.repositories.user_repository import UserRepository
            from app.di.container import container
            
            user_repo = container.resolve("user_repository")
            sender_user = await user_repo.findByEmail(user_id)
            
            if not sender_user:
                await manager.send_personal_message(
                    SocketResponse(type="error", data={}, status="error", message="Sender user not found").model_dump(),
                    client_id
                )
                return
            
            # Send the message via chat mediator for persistence and WebSocket delivery
            result = await self.chat_mediator.send_message(sender_user.id, message_data)
            
            # Confirm to sender
            await manager.send_personal_message(
                SocketResponse(type="success", data={"message_id": str(result.id)}, status="success", message="Message sent").model_dump(),
                client_id
            )
            
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            await manager.send_personal_message(
                SocketResponse(type="error", data={}, status="error", message=str(e)).model_dump(),
                client_id
            )
    
    async def _handle_typing_indicator(self, client_id: str, payload: Dict[str, Any], user_id: str):
        """Handle typing indicator"""
        try:
            receiver_id = payload.get("receiver_id")
            is_typing = payload.get("is_typing", True)
            
            if receiver_id:
                await manager.send_to_user({
                    "type": "typing",
                    "sender_id": user_id,
                    "is_typing": is_typing
                }, receiver_id)
                
        except Exception as e:
            logger.error(f"Error handling typing indicator: {e}")
    
    async def _handle_read_receipt(self, client_id: str, payload: Dict[str, Any], user_id: str):
        """Handle read receipt"""
        try:
            message_id = payload.get("message_id")
            
            if message_id:
                # Notify the original sender that their message was read
                await manager.send_to_user({
                    "type": "read_receipt",
                    "message_id": message_id,
                    "reader_id": user_id
                }, payload.get("sender_id"))
                
        except Exception as e:
            logger.error(f"Error handling read receipt: {e}")

# Global instance
handler = SocketHandler()
