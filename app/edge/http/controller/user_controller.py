from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger

logger = get_logger(__name__)

class UserController:
    @inject
    def __init__(self, user_mediator = Provide["user_mediator"]):
        self.user_mediator = user_mediator

    async def list_users(self, filters: dict = None, offset: int = 0, limit: int = 10):
        try:
            logger.info("UserController: Listing users...")
            
            result = await self.user_mediator.list_users(filters, offset, limit)
            
            logger.info("UserController: Listed users successfully.")
            
            return result 

        except Exception as e:
            logger.error("UserController: Failed to list users.", exc_info=True)
            raise e

    async def get_user(self, user_id: str):
        try:
            logger.info("UserController: Getting user...")
            
            user = await self.user_mediator.get_user(user_id)
            
            logger.info("UserController: Got user successfully.")
            
            return user

        except Exception as e:
            logger.error("UserController: Failed to get user.", exc_info=True)
            raise e

    async def create_user(self, user_data):
        try:
            logger.info("UserController: Creating user...")
            
            user = await self.user_mediator.create_user(user_data)
            
            logger.info("UserController: Created user successfully.")

            return user 

        except Exception as e:
            logger.error("UserController: Failed to create user.", exc_info=True)
            raise e

    async def update_user(self, user_id: str, user_data):
        try:
            logger.info("UserController: Updating user...")
            
            user = await self.user_mediator.update_user(user_id, user_data)
            
            logger.info("UserController: Updated user successfully.")

            return user 

        except Exception as e:
            logger.error("UserController: Failed to update user.", exc_info=True)
            raise e

    async def get_profile(self, current_user_id):
        try:
            return await self.user_mediator.get_profile(current_user_id)
        except Exception as e:
            logger.error("UserController: Failed to get profile.", exc_info=True)
            raise e

    async def update_profile(self, current_user_id, data):
        try:
            return await self.user_mediator.update_profile(current_user_id, data)
        except Exception as e:
            logger.error("UserController: Failed to update profile.", exc_info=True)
            raise e

    async def change_password(self, current_user_id, data):
        try:
            return await self.user_mediator.change_password(current_user_id, data)
        except Exception as e:
            logger.error("UserController: Failed to change password.", exc_info=True)
            raise e

    async def delete_user(self, user_id: str):
        try:
            logger.info("UserController: Deleting user...")
            
            result = await self.user_mediator.delete_user(user_id)
            
            logger.info("UserController: Deleted user successfully.")

            return result 

        except Exception as e:
            logger.error("UserController: Failed to delete user.", exc_info=True)
            raise e
