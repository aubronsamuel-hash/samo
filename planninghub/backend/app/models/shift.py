import enum
import uuid

from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from ..database import Base


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


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    call_time = Column(DateTime(timezone=True), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    break_times = Column(JSON, default=list)
    resources = Column(JSON, default=list)
    economic_value = Column(JSON, default=dict)
    status = Column(SQLEnum(ShiftStatus), default=ShiftStatus.PLANNED)
    priority = Column(SQLEnum(ShiftPriority), default=ShiftPriority.MEDIUM)
    conflicts = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(Integer, default=1)
