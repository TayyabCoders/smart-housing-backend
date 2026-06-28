from app.schemas.common_schema import BBox, PaginatedResponse
from app.schemas.dashboard_schema import DashboardStatsResponse
from app.schemas.vehicle_detection_schema import (
    MatchedVehicleInfo,
    VehicleDetectionResponse,
    VehicleDetectionActionRequest,
    VehicleDetectionListResponse,
)
from app.schemas.face_detection_schema import (
    MatchedPersonInfo,
    FaceDetectionResponse,
    FaceDetectionActionRequest,
    FaceDetectionListResponse,
)
from app.schemas.alert_schema import (
    AlertVehicleDetectionInfo,
    AlertFaceDetectionInfo,
    AlertResponse,
    AlertDismissRequest,
    AlertResolveRequest,
    AlertListResponse,
)
from app.schemas.person_schema import (
    PersonResponse,
    PersonCreateRequest,
    PersonUpdateRequest,
)
from app.schemas.vehicle_schema import (
    VehicleResponse,
    VehicleCreateRequest,
    VehicleUpdateRequest,
)
from app.schemas.camera_schema import (
    CameraResponse,
    CameraCreateRequest,
    CameraUpdateRequest,
)
from app.schemas.complaint_schema import (
    Complaint,
    ComplaintCreate,
    ComplaintUpdate,
)

__all__ = [
    # Common
    "BBox",
    "PaginatedResponse",
    # Dashboard
    "DashboardStatsResponse",
    # Vehicle Detection
    "MatchedVehicleInfo",
    "VehicleDetectionResponse",
    "VehicleDetectionActionRequest",
    "VehicleDetectionListResponse",
    # Face Detection
    "MatchedPersonInfo",
    "FaceDetectionResponse",
    "FaceDetectionActionRequest",
    "FaceDetectionListResponse",
    # Alerts
    "AlertVehicleDetectionInfo",
    "AlertFaceDetectionInfo",
    "AlertResponse",
    "AlertDismissRequest",
    "AlertResolveRequest",
    "AlertListResponse",
    # Persons
    "PersonResponse",
    "PersonCreateRequest",
    "PersonUpdateRequest",
    # Vehicles
    "VehicleResponse",
    "VehicleCreateRequest",
    "VehicleUpdateRequest",
    # Cameras
    "CameraResponse",
    "CameraCreateRequest",
    "CameraUpdateRequest",
    # Complaints
    "Complaint",
    "ComplaintCreate",
    "ComplaintUpdate",
]
