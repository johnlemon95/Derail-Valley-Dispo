from enum import Enum


class JobStatus(str, Enum):
    UNCLAIMED = "UNCLAIMED"
    CLAIMED = "CLAIMED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class JobType(str, Enum):
    SHUNTING = "SH"
    LOGISTICS = "LOG"
    FREIGHT = "FR"
    MULTI = "MULTI"
    CUSTOM = "CUST"


class VehicleType(str, Enum):
    BE2 = "BE2"
    DE2 = "DE2"
    DH4 = "DH4"
    DE6 = "DE6"
    DE6_SLUG = "DE6_SLUG"
    S060 = "S060"
    S282 = "S282"
    HC = "HC"


class DriveType(str, Enum):
    DIESEL_ELECTRIC = "Diesel-Elektrik"
    DIESEL_HYDRAULIC = "Diesel-Hydraulik"
    ELECTRIC_BATTERY = "Elektro (Batterie)"
    STEAM = "Dampf"
    MANUAL = "Manuell"
    TRACTION_EXTENSION = "Traktionserweiterung"


class StationCode(str, Enum):
    HB = "HB"
    GF = "GF"
    CS = "CS"
    FF = "FF"
    SW = "SW"
    MF = "MF"
    CM = "CM"
    IME = "IME"
    IMW = "IMW"
    FS = "FS"
    FM = "FM"
    OWC = "OWC"
    OR = "OR"


class UserRole(str, Enum):
    ADMIN = "Admin"
    OPERATOR = "Operator"


class TrackStatus(str, Enum):
    FREE = "FREE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"


class WSEvent(str, Enum):
    JOB_CLAIMED = "job_claimed"
    JOB_RELEASED = "job_released"
    JOB_IN_TRANSIT = "job_in_transit"
    JOB_DELIVERED = "job_delivered"
    JOB_CREATED = "job_created"
    JOB_CANCELLED = "job_cancelled"
    VEHICLE_UPDATED = "vehicle_updated"
    TRACK_UPDATED = "track_updated"
    PLAYER_CONNECTED = "player_connected"
    PLAYER_DISCONNECTED = "player_disconnected"
