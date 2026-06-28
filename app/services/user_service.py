from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import HTTPException, status

from app.schemas.user_schema import UserCreate, UserUpdate, User
from app.di.container import container
import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class UserService:
    @inject
    def __init__(
        self,
        user_repository = Provide["user_repository"],
        prometheus = Provide["prometheus"],
        security_util = Provide["security_util"],
    ):
        self.user_repository = user_repository
        self.prometheus = prometheus
        self.security_util = security_util
    
    async def list_users(self, filters: dict = None, offset: int = 0, limit: int = 10) -> Dict[str, Any]:
        try:
            logger.info("UserService: Listing users...")
            
            result = await self.user_repository.findAndCountAll(filters, offset, limit)
            
            # Convert SQLAlchemy User objects to Pydantic User schemas
            user_schemas = [User.model_validate(user) for user in result['rows']]
            result['rows'] = user_schemas
            
            logger.info(f"UserService: Listed users successfully. Total: {result['total']}")
            
            # Record business event
            self.prometheus.record_business_event("user_list", "success")
            
            return result
        
        except Exception as e:
            logger.error("UserService: Failed to list users.", exc_info=True)
            raise e

    async def get_user(self, user_id: str) -> Any:
        try:
            logger.info("UserService: Getting user...")
            
            # Convert string to UUID if needed
            try:
                user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )
            
            user = await self.user_repository.findById(user_uuid)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            logger.info(f"UserService: Got user successfully: {user.username}")
            
            # Convert SQLAlchemy User to Pydantic User schema
            return User.model_validate(user)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("UserService: Failed to get user.", exc_info=True)
            raise e

    async def create_user(self, user_data: UserCreate) -> Any:
        try:
            logger.info("UserService: Creating user...")
            
            # Check if user already exists
            if await self.user_repository.findByUsername(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
        
            if await self.user_repository.findByEmail(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Hash password and create user
            user_dict = user_data.model_dump()
            password = user_dict.pop("password")
            user_dict["hashed_password"] = self.security_util.get_password_hash(password)
            
            user = await self.user_repository.create(user_dict)
            logger.info(f"UserService: User created successfully: {user.username}")
            
            # Record business event
            self.prometheus.record_business_event("user_creation", "success")
            
            # Convert SQLAlchemy User to Pydantic User schema
            return User.model_validate(user)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("UserService: Failed to create user.", exc_info=True)
            raise e

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Any:
        try:
            logger.info("UserService: Updating user...")
            
            # Convert string to UUID if needed
            try:
                user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )
            
            # Check if user exists
            existing_user = await self.user_repository.findById(user_uuid)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Prepare update data
            update_data = user_data.model_dump(exclude_unset=True)
            
            # Hash password if provided
            if "password" in update_data:
                update_data["hashed_password"] = self.security_util.get_password_hash(update_data.pop("password"))
            
            # Update user
            user = await self.user_repository.update(user_uuid, update_data)
            logger.info(f"UserService: User updated successfully: {user.username}")
            
            # Record business event
            self.prometheus.record_business_event("user_update", "success")
            
            # Convert SQLAlchemy User to Pydantic User schema
            return User.model_validate(user)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("UserService: Failed to update user.", exc_info=True)
            raise e

    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        try:
            logger.info("UserService: Deleting user...")
            
            # Convert string to UUID if needed
            try:
                user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )
            
            # Check if user exists
            existing_user = await self.user_repository.findById(user_uuid)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Delete user
            result = await self.user_repository.delete(user_uuid)
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete user"
                )
            
            logger.info(f"UserService: User deleted successfully: {existing_user.username}")
            
            # Record business event
            self.prometheus.record_business_event("user_deletion", "success")
            
            return {"message": "User deleted successfully"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("UserService: Failed to delete user.", exc_info=True)
            raise e
