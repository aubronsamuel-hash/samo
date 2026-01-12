from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, RootModel, model_validator


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    roles: List[str] = []
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []
    specializations: List[Dict[str, Any]] = []
    availability: Dict[str, List[str]] = {}
    employment_contract: Dict[str, Any] = {}

    model_config = {"from_attributes": True}


class AvailabilityPayload(RootModel[Dict[str, Optional[List[str]]]]):
    pass


class AvailabilityWarning(BaseModel):
    date: str
    message: str
    severity: str


class AvailabilityUpdateResponse(BaseModel):
    status: str
    availability: Dict[str, List[str]]
    warnings: List[AvailabilityWarning] = []


class BreakTime(BaseModel):
    start: datetime
    end: datetime
    mandatory: bool = False


class ResourceItem(BaseModel):
    id: UUID
    type: str
    role: Optional[str] = None
    required_skills: List[str] = []
    quantity: int = 1


class EconomicValueBreakdown(BaseModel):
    labor_cost: Optional[float] = None
    equipment_cost: Optional[float] = None
    transport_cost: Optional[float] = None
    meal_allowance: Optional[float] = None
    overtime_cost: Optional[float] = None


class EconomicValue(BaseModel):
    base_rate: float
    budget_line: str
    total_amount: Optional[float] = None
    equipment_rate: Optional[float] = None
    breakdown: Optional[EconomicValueBreakdown] = None


class ShiftMetadata(BaseModel):
    technical_rider: Optional[str] = None
    stage_plot: Optional[str] = None
    cable_plan: Optional[str] = None


class ShiftCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    event_id: UUID
    call_time: Optional[datetime] = None
    start_time: datetime
    end_time: datetime
    break_times: List[BreakTime] = []
    resources: List[ResourceItem]
    economic_value: EconomicValue
    priority: str = "medium"
    metadata: Optional[ShiftMetadata] = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.call_time and self.call_time > self.start_time:
            raise ValueError("call_time doit etre avant start_time")
        if self.end_time <= self.start_time:
            raise ValueError("end_time doit etre apres start_time")
        for pause in self.break_times:
            if pause.start >= pause.end:
                raise ValueError("break_times doit avoir start < end")
            if pause.start < self.start_time or pause.end > self.end_time:
                raise ValueError("break_times doit etre dans la plage du shift")
        return self


class ConflictItem(BaseModel):
    resource_id: UUID
    resource_type: str
    shift_id: Optional[UUID] = None
    severity: str


class WarningItem(BaseModel):
    code: str
    message: str
    severity: str


class ShiftResponse(BaseModel):
    id: UUID
    status: str
    conflicts: List[ConflictItem] = []
    warnings: List[WarningItem] = []
    economic_value: Dict
    created_at: Optional[datetime] = None
    version: int

    model_config = {"from_attributes": True}


class EquipmentStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    MAINTENANCE = "maintenance"
    BROKEN = "broken"


class EquipmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: str
    subcategory: str
    status: EquipmentStatus = EquipmentStatus.AVAILABLE
    quantity: int = Field(default=1, ge=1)
    location: Dict[str, Any] = {}
    availability: List[Dict[str, Any]] = []
    specifications: Dict[str, Any] = {}
    maintenance: Dict[str, Any] = {}
    maintenance_log: List[Dict[str, Any]] = []
    license_required: Optional[str] = None


class EquipmentResponse(BaseModel):
    id: UUID
    name: str
    category: str
    subcategory: str
    status: EquipmentStatus
    quantity: int
    location: Dict[str, Any]
    availability: List[Dict[str, Any]]
    specifications: Dict[str, Any]
    maintenance: Dict[str, Any]
    maintenance_log: List[Dict[str, Any]]
    license_required: Optional[str] = None
    organization_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EquipmentListResponse(BaseModel):
    count: int
    results: List[EquipmentResponse]
