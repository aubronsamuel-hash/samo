import enum
import uuid

from sqlalchemy import Column, Date, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from .database import Base


class ShiftStatus(str, enum.Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    CALL_ISSUED = "call_issued"
    IN_PROGRESS = "in_progress"
    BREAK = "break"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class ShiftPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EquipmentStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    MAINTENANCE = "maintenance"
    BROKEN = "broken"


class EventStatus(str, enum.Enum):
    PLANNING = "planning"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    roles = Column(JSON, default=list)
    specializations = Column(JSON, default=list)
    availability = Column(JSON, default=dict)
    employment_contract = Column(JSON, default=dict)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    license_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    status = Column(SQLEnum(EquipmentStatus), default=EquipmentStatus.AVAILABLE)
    quantity = Column(Integer, default=1)
    location = Column(JSON, default=dict)
    availability = Column(JSON, default=list)
    specifications = Column(JSON, default=dict)
    maintenance = Column(JSON, default=dict)
    maintenance_log = Column(JSON, default=list)
    license_required = Column(String, nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    call_time = Column(DateTime(timezone=True), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    break_times = Column(JSON, default=list)
    resources = Column(JSON, default=list)
    economic_value = Column(JSON, default=dict)
    status = Column(SQLEnum(ShiftStatus), default=ShiftStatus.DRAFT)
    priority = Column(SQLEnum(ShiftPriority), default=ShiftPriority.MEDIUM)
    conflicts = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(Integer, default=1)

    created_by_user = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assignee_id])
    event = relationship("Event", back_populates="shifts")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    venue = Column(JSON, default=dict)
    technical_requirements = Column(JSON, default=dict)
    budget = Column(JSON, default=dict)
    status = Column(SQLEnum(EventStatus), default=EventStatus.PLANNING)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shifts = relationship("Shift", back_populates="event")
