from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, or_, and_
from app.repositories.base_repository import BaseRepository
from app.models.chat import Conversation
from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from typing import Any

logger = get_logger(__name__)


class ConversationRepository(BaseRepository[Conversation]):
    @inject
    def __init__(self, database = Provide["database"], cache: Any = Provide["cache"]):
        super().__init__(Conversation, database, cache)

    async def findConversation(self, user1_id: UUID, user2_id: UUID) -> Optional[Conversation]:
        """Find conversation between two users"""
        try:
            logger.info("ConversationRepository: Finding conversation...")
            
            async with self.database.get_session("read") as session:
                stmt = select(Conversation).where(
                    or_(
                        and_(Conversation.user1_id == user1_id, Conversation.user2_id == user2_id),
                        and_(Conversation.user1_id == user2_id, Conversation.user2_id == user1_id)
                    )
                )
                
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                logger.info("ConversationRepository: Found conversation.")
                
                return conversation
        
        except Exception as e:
            logger.error("ConversationRepository: Failed to find conversation.", exc_info=True)
            raise e

    async def findUserConversations(self, user_id: UUID) -> List[Conversation]:
        """Find all conversations for a user"""
        try:
            logger.info("ConversationRepository: Finding user conversations...")
            
            async with self.database.get_session("read") as session:
                stmt = select(Conversation).where(
                    or_(
                        Conversation.user1_id == user_id,
                        Conversation.user2_id == user_id
                    )
                ).order_by(Conversation.last_message_time.desc())
                
                result = await session.execute(stmt)
                conversations = result.scalars().all()
                
                logger.info(f"ConversationRepository: Found {len(conversations)} conversations.")
                
                return list(conversations)
        
        except Exception as e:
            logger.error("ConversationRepository: Failed to find user conversations.", exc_info=True)
            raise e

    async def updateUnreadCount(self, conversation_id: UUID, user_id: UUID, count: int) -> Optional[Conversation]:
        """Update unread count for a specific user in conversation"""
        try:
            logger.info("ConversationRepository: Updating unread count...")
            
            async with self.database.get_session("write") as session:
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    return None
                
                if conversation.user1_id == user_id:
                    conversation.unread_count_user1 = count
                else:
                    conversation.unread_count_user2 = count
                
                session.add(conversation)
                await session.commit()
                await session.refresh(conversation)
                
                logger.info("ConversationRepository: Updated unread count.")
                
                return conversation
        
        except Exception as e:
            await session.rollback()
            logger.error("ConversationRepository: Failed to update unread count.", exc_info=True)
            raise e
