from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from uuid import UUID

logger = get_logger(__name__)


class ChatMediator:
    @inject
    def __init__(
        self,
        chat_service = Provide["chat_service"]
    ):
        self.chat_service = chat_service

    async def send_message(self, sender_id: UUID, message_data):
        try:
            logger.info("ChatMediator: Sending message...")
            
            result = await self.chat_service.send_message(sender_id, message_data)
            
            logger.info("ChatMediator: Message sent successfully.")
            
            return result
        
        except Exception as e:
            logger.error("ChatMediator: Failed to send message.", exc_info=True)
            raise e

    async def get_conversations(self, user_id: UUID):
        try:
            logger.info("ChatMediator: Getting conversations...")
            
            result = await self.chat_service.get_conversations(user_id)
            
            logger.info("ChatMediator: Got conversations successfully.")
            
            return result
        
        except Exception as e:
            logger.error("ChatMediator: Failed to get conversations.", exc_info=True)
            raise e

    async def get_messages(self, user_id: UUID, other_user_id: UUID, limit: int = 50, offset: int = 0):
        try:
            logger.info("ChatMediator: Getting messages...")
            
            result = await self.chat_service.get_messages(user_id, other_user_id, limit, offset)
            
            logger.info("ChatMediator: Got messages successfully.")
            
            return result
        
        except Exception as e:
            logger.error("ChatMediator: Failed to get messages.", exc_info=True)
            raise e

    async def mark_message_read(self, message_id: UUID, user_id: UUID):
        try:
            logger.info("ChatMediator: Marking message as read...")
            
            result = await self.chat_service.mark_message_read(message_id, user_id)
            
            logger.info("ChatMediator: Message marked as read successfully.")
            
            return result
        
        except Exception as e:
            logger.error("ChatMediator: Failed to mark message as read.", exc_info=True)
            raise e
