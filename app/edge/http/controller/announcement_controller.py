from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from app.models.user_model import User

logger = get_logger(__name__)

class AnnouncementController:
    @inject
    def __init__(self, announcement_mediator = Provide["announcement_mediator"]):
        self.announcement_mediator = announcement_mediator

    async def list_announcements(self, offset: int = 0, limit: int = 10):
        try:
            logger.info("AnnouncementController: Listing announcements...")

            result = await self.announcement_mediator.list_announcements(offset, limit)

            logger.info("AnnouncementController: Listed announcements successfully.")

            return result

        except Exception as e:
            logger.error("AnnouncementController: Failed to list announcements.", exc_info=True)
            raise e

    async def get_announcement(self, announcement_id: str):
        try:
            logger.info("AnnouncementController: Getting announcement...")

            announcement = await self.announcement_mediator.get_announcement(announcement_id)

            logger.info("AnnouncementController: Got announcement successfully.")

            return announcement

        except Exception as e:
            logger.error("AnnouncementController: Failed to get announcement.", exc_info=True)
            raise e

    async def create_announcement(self, announcement_data, current_user: User):
        try:
            logger.info("AnnouncementController: Creating announcement...")

            announcement = await self.announcement_mediator.create_announcement(announcement_data, current_user)

            logger.info("AnnouncementController: Created announcement successfully.")

            return announcement

        except Exception as e:
            logger.error("AnnouncementController: Failed to create announcement.", exc_info=True)
            raise e

    async def update_announcement(self, announcement_id: str, announcement_data):
        try:
            logger.info("AnnouncementController: Updating announcement...")

            announcement = await self.announcement_mediator.update_announcement(announcement_id, announcement_data)

            logger.info("AnnouncementController: Updated announcement successfully.")

            return announcement

        except Exception as e:
            logger.error("AnnouncementController: Failed to update announcement.", exc_info=True)
            raise e

    async def delete_announcement(self, announcement_id: str):
        try:
            logger.info("AnnouncementController: Deleting announcement...")

            result = await self.announcement_mediator.delete_announcement(announcement_id)

            logger.info("AnnouncementController: Deleted announcement successfully.")

            return result

        except Exception as e:
            logger.error("AnnouncementController: Failed to delete announcement.", exc_info=True)
            raise e
