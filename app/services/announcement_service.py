from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status

from app.schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate, Announcement as AnnouncementSchema
from app.di.container import container
from app.models.user_model import User
import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class AnnouncementService:
    @inject
    def __init__(
        self,
        announcement_repository = Provide["announcement_repository"],
        prometheus = Provide["prometheus"],
    ):
        self.announcement_repository = announcement_repository
        self.prometheus = prometheus

    async def list_announcements(self, offset: int = 0, limit: int = 10) -> Dict[str, Any]:
        try:
            logger.info("AnnouncementService: Listing announcements...")

            result = await self.announcement_repository.findAndCountAll({}, offset, limit)

            announcement_schemas = [AnnouncementSchema.model_validate(announcement) for announcement in result['rows']]
            result['rows'] = announcement_schemas

            logger.info(f"AnnouncementService: Listed announcements successfully. Total: {result['total']}")

            self.prometheus.record_business_event("announcement_list", "success")

            return result

        except Exception as e:
            logger.error("AnnouncementService: Failed to list announcements.", exc_info=True)
            raise e

    async def get_announcement(self, announcement_id: str) -> Any:
        try:
            logger.info("AnnouncementService: Getting announcement...")

            try:
                announcement_uuid = UUID(announcement_id) if isinstance(announcement_id, str) else announcement_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid announcement ID format"
                )

            announcement = await self.announcement_repository.findById(announcement_uuid)

            if not announcement:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Announcement not found"
                )

            logger.info(f"AnnouncementService: Got announcement successfully: {announcement.id}")

            return AnnouncementSchema.model_validate(announcement)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("AnnouncementService: Failed to get announcement.", exc_info=True)
            raise e

    async def create_announcement(self, announcement_data: AnnouncementCreate, current_user: User) -> Any:
        try:
            logger.info("AnnouncementService: Creating announcement...")

            announcement_dict = announcement_data.model_dump()
            announcement_dict["created_by"] = str(current_user.id)

            announcement = await self.announcement_repository.create(announcement_dict)
            logger.info(f"AnnouncementService: Announcement created successfully: {announcement.id}")

            self.prometheus.record_business_event("announcement_creation", "success")

            return AnnouncementSchema.model_validate(announcement)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("AnnouncementService: Failed to create announcement.", exc_info=True)
            raise e

    async def update_announcement(self, announcement_id: str, announcement_data: AnnouncementUpdate) -> Any:
        try:
            logger.info("AnnouncementService: Updating announcement...")

            try:
                announcement_uuid = UUID(announcement_id) if isinstance(announcement_id, str) else announcement_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid announcement ID format"
                )

            existing_announcement = await self.announcement_repository.findById(announcement_uuid)
            if not existing_announcement:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Announcement not found"
                )

            update_data = announcement_data.model_dump(exclude_unset=True)

            announcement = await self.announcement_repository.update(announcement_uuid, update_data)
            logger.info(f"AnnouncementService: Announcement updated successfully: {announcement.id}")

            self.prometheus.record_business_event("announcement_update", "success")

            return AnnouncementSchema.model_validate(announcement)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("AnnouncementService: Failed to update announcement.", exc_info=True)
            raise e

    async def delete_announcement(self, announcement_id: str) -> Dict[str, Any]:
        try:
            logger.info("AnnouncementService: Deleting announcement...")

            try:
                announcement_uuid = UUID(announcement_id) if isinstance(announcement_id, str) else announcement_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid announcement ID format"
                )

            existing_announcement = await self.announcement_repository.findById(announcement_uuid)
            if not existing_announcement:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Announcement not found"
                )

            result = await self.announcement_repository.delete(announcement_uuid)

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete announcement"
                )

            logger.info(f"AnnouncementService: Announcement deleted successfully: {existing_announcement.id}")

            self.prometheus.record_business_event("announcement_deletion", "success")

            return {"message": "Announcement deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error("AnnouncementService: Failed to delete announcement.", exc_info=True)
            raise e
