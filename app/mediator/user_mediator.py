from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger

logger = get_logger(__name__)

class UserMediator:
    @inject
    def __init__(
        self,
        user_service = Provide["user_service"]
    ):
        self.user_service = user_service

    async def list_users(self, filters: dict = None, offset: int = 0, limit: int = 10):
        try:
            logger.info("UserMediator: Listing users...")
            
            result = await self.user_service.list_users(filters, offset, limit)
            
            logger.info("UserMediator: Listed users successfully.")
            
            return result
        
        except Exception as e:
            logger.error("UserMediator: Failed to list users.", exc_info=True)
            raise e

    async def get_user(self, user_id: str):
        try:
            logger.info("UserMediator: Getting user...")
            
            result = await self.user_service.get_user(user_id)
            
            logger.info("UserMediator: Got user successfully.")
            
            return result
        
        except Exception as e:
            logger.error("UserMediator: Failed to get user.", exc_info=True)
            raise e

    async def create_user(self, user_data):
        try:
            logger.info("UserMediator: Creating user...")
            
            user = await self.user_service.create_user(user_data)
            
            logger.info("UserMediator: User created successfully.")
            
            return user
        
        except Exception as e:
            logger.error("UserMediator: Failed to create user.", exc_info=True)
            raise e

    async def update_user(self, user_id: str, user_data):
        try:
            logger.info("UserMediator: Updating user...")
            
            user = await self.user_service.update_user(user_id, user_data)
            
            logger.info("UserMediator: User updated successfully.")
            
            return user
        
        except Exception as e:
            logger.error("UserMediator: Failed to update user.", exc_info=True)
            raise e

    async def delete_user(self, user_id: str):
        try:
            logger.info("UserMediator: Deleting user...")
            
            result = await self.user_service.delete_user(user_id)
            
            logger.info("UserMediator: User deleted successfully.")
            
            return result
        
        except Exception as e:
            logger.error("UserMediator: Failed to delete user.", exc_info=True)
            raise e
