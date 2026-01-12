from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    roles: List[str] = []
    first_name: Optional[str] = None
    last_name: Optional[str] = None


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
    shift_id: UUID
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
