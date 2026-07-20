from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from app.models.user_model import User

logger = get_logger(__name__)

class AnnouncementMediator:
    @inject
    def __init__(
        self,
        announcement_service = Provide["announcement_service"]
    ):
        self.announcement_service = announcement_service

    async def list_announcements(self, offset: int = 0, limit: int = 10):
        try:
            logger.info("AnnouncementMediator: Listing announcements...")

            result = await self.announcement_service.list_announcements(offset, limit)

            logger.info("AnnouncementMediator: Listed announcements successfully.")

            return result

        except Exception as e:
            logger.error("AnnouncementMediator: Failed to list announcements.", exc_info=True)
            raise e

    async def get_announcement(self, announcement_id: str):
        try:
            logger.info("AnnouncementMediator: Getting announcement...")

            result = await self.announcement_service.get_announcement(announcement_id)

            logger.info("AnnouncementMediator: Got announcement successfully.")

            return result

        except Exception as e:
            logger.error("AnnouncementMediator: Failed to get announcement.", exc_info=True)
            raise e

    async def create_announcement(self, announcement_data, current_user: User):
        try:
            logger.info("AnnouncementMediator: Creating announcement...")

            announcement = await self.announcement_service.create_announcement(announcement_data, current_user)

            logger.info("AnnouncementMediator: Announcement created successfully.")

            return announcement

        except Exception as e:
            logger.error("AnnouncementMediator: Failed to create announcement.", exc_info=True)
            raise e

    async def update_announcement(self, announcement_id: str, announcement_data):
        try:
            logger.info("AnnouncementMediator: Updating announcement...")

            announcement = await self.announcement_service.update_announcement(announcement_id, announcement_data)

            logger.info("AnnouncementMediator: Announcement updated successfully.")

            return announcement

        except Exception as e:
            logger.error("AnnouncementMediator: Failed to update announcement.", exc_info=True)
            raise e

    async def delete_announcement(self, announcement_id: str):
        try:
            logger.info("AnnouncementMediator: Deleting announcement...")

            result = await self.announcement_service.delete_announcement(announcement_id)

            logger.info("AnnouncementMediator: Announcement deleted successfully.")

            return result

        except Exception as e:
            logger.error("AnnouncementMediator: Failed to delete announcement.", exc_info=True)
            raise e
