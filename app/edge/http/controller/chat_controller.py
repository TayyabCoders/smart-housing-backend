from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from uuid import UUID

logger = get_logger(__name__)


class ChatController:
    @inject
    def __init__(self, chat_mediator = Provide["chat_mediator"]):
        self.chat_mediator = chat_mediator

    async def send_message(self, sender_id: UUID, message_data):
        try:
            logger.info("ChatController: Sending message...")
            
            result = await self.chat_mediator.send_message(sender_id, message_data)
            
            logger.info("ChatController: Message sent successfully.")
            
            return result 

        except Exception as e:
            logger.error("ChatController: Failed to send message.", exc_info=True)
            raise e

    async def get_conversations(self, user_id: UUID):
        try:
            logger.info("ChatController: Getting conversations...")
            
            result = await self.chat_mediator.get_conversations(user_id)
            
            logger.info("ChatController: Got conversations successfully.")
            
            return result 

        except Exception as e:
            logger.error("ChatController: Failed to get conversations.", exc_info=True)
            raise e

    async def get_messages(self, user_id: UUID, other_user_id: UUID, limit: int = 50, offset: int = 0):
        try:
            logger.info("ChatController: Getting messages...")
            
            result = await self.chat_mediator.get_messages(user_id, other_user_id, limit, offset)
            
            logger.info("ChatController: Got messages successfully.")
            
            return result 

        except Exception as e:
            logger.error("ChatController: Failed to get messages.", exc_info=True)
            raise e

    async def mark_message_read(self, message_id: UUID, user_id: UUID):
        try:
            logger.info("ChatController: Marking message as read...")
            
            result = await self.chat_mediator.mark_message_read(message_id, user_id)
            
            logger.info("ChatController: Message marked as read successfully.")
            
            return result 

        except Exception as e:
            logger.error("ChatController: Failed to mark message as read.", exc_info=True)
            raise e
