import enum


class CameraType(str, enum.Enum):
    PLATE = "plate"
    FACE = "face"
    BOTH = "both"


class VehicleStatus(str, enum.Enum):
    RESIDENT = "resident"
    VISITOR = "visitor"
    STAFF = "staff"
    BLACKLIST = "blacklist"


class DetectionStatus(str, enum.Enum):
    RESIDENT = "resident"
    VISITOR = "visitor"
    STAFF = "staff"
    BLACKLIST = "blacklist"
    UNKNOWN = "unknown"


class AlertKind(str, enum.Enum):
    BLACKLIST = "blacklist"
    UNKNOWN = "unknown"
    TAILGATE = "tailgate"
    EXPIRED = "expired"


class AlertSeverity(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ActionType(str, enum.Enum):
    OPEN_GATE = "open_gate"
    BLOCK = "block"
    MARK_VISITOR = "mark_visitor"
    ALLOW = "allow"
    DENY = "deny"
    FLAG_UNKNOWN = "flag_unknown"
    REGISTER_VISITOR = "register_visitor"


class PersonRole(str, enum.Enum):
    RESIDENT = "resident"
    STAFF = "staff"
    VISITOR = "visitor"


class VisitorApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
