from typing import Any

from app.models.user_model import User
from app.models.base_model import Base
from app.models.camera import Camera
from app.models.vehicle import Vehicle
from app.models.vehicle_detection import VehicleDetection
from app.models.person import Person
from app.models.face_embedding import FaceEmbedding
from app.models.face_detection import FaceDetection
from app.models.alert import Alert
from app.models.visitor_approval import VisitorApproval
from app.models.complaint_model import Complaint
from app.models.election import Election
from app.models.candidate import Candidate
from app.models.vote import Vote
from app.models.activity_log import ActivityLog
from app.models.chat import Message, Conversation
from app.models.parking_record_model import ParkingRecord
from app.models.cnic_record_model import CnicRecord
from app.models.access_log import AccessLog


async def initialize_models(database: Any) -> None:
    """Initialize database models by creating all tables.

    This uses the master engine from the Database wrapper to run
    SQLAlchemy's metadata.create_all synchronously within an async
    connection context.
    """
    # database is expected to be an instance of app.configs.database_config.Database
    engine = getattr(database, "master_engine", None)
    if engine is None:
        raise RuntimeError("Database master_engine is not initialized")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = [
    "User",
    "Camera",
    "Vehicle",
    "VehicleDetection",
    "Person",
    "FaceEmbedding",
    "FaceDetection",
    "Alert",
    "VisitorApproval",
    "Complaint",
    "Election",
    "Candidate",
    "Vote",
    "ActivityLog",
    "Message",
    "Conversation",
    "ParkingRecord",
    "CnicRecord",
    "AccessLog",
    "initialize_models",
]
