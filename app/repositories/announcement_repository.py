from typing import Optional, Any
from app.repositories.base_repository import BaseRepository
from app.models.announcement_model import Announcement

from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger

logger = get_logger(__name__)

class AnnouncementRepository(BaseRepository[Announcement]):
    @inject
    def __init__(self, database = Provide["database"], cache: Optional[Any] = Provide["cache"]):
        super().__init__(Announcement, database, cache)
