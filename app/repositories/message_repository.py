from typing import List
from uuid import UUID
from sqlalchemy import select, or_, and_
from app.repositories.base_repository import BaseRepository
from app.models.chat import Message
from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from typing import Any

logger = get_logger(__name__)


class MessageRepository(BaseRepository[Message]):
    @inject
    def __init__(self, database = Provide["database"], cache: Any = Provide["cache"]):
        super().__init__(Message, database, cache)

    async def findConversationMessages(
        self, 
        user1_id: UUID, 
        user2_id: UUID, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Message]:
        """Find all messages between two users"""
        try:
            logger.info("MessageRepository: Finding conversation messages...")
            
            async with self.database.get_session("read") as session:
                stmt = select(Message).where(
                    or_(
                        and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                        and_(Message.sender_id == user2_id, Message.receiver_id == user1_id)
                    )
                ).order_by(Message.timestamp.desc()).offset(offset).limit(limit)
                
                result = await session.execute(stmt)
                messages = result.scalars().all()
                
                logger.info(f"MessageRepository: Found {len(messages)} messages.")
                
                return list(messages)
        
        except Exception as e:
            logger.error("MessageRepository: Failed to find conversation messages.", exc_info=True)
            raise e

    async def markAsRead(self, sender_id: UUID, receiver_id: UUID) -> int:
        """Mark all messages from sender to receiver as read"""
        try:
            logger.info("MessageRepository: Marking messages as read...")
            
            async with self.database.get_session("write") as session:
                from sqlalchemy import update
                
                stmt = update(Message).where(
                    and_(
                        Message.sender_id == sender_id,
                        Message.receiver_id == receiver_id,
                        Message.is_read == False
                    )
                ).values(is_read=True)
                
                result = await session.execute(stmt)
                await session.commit()
                
                logger.info(f"MessageRepository: Marked {result.rowcount} messages as read.")
                
                return result.rowcount
        
        except Exception as e:
            await session.rollback()
            logger.error("MessageRepository: Failed to mark messages as read.", exc_info=True)
            raise e
