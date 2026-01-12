from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class EquipmentAvailability(BaseModel):
    start_time: datetime
    end_time: datetime
    status: str
    event_id: Optional[UUID] = None


class EquipmentResponse(BaseModel):
    id: UUID
    name: str
    category: str
    subcategory: str
    availability: List[EquipmentAvailability] = []

    model_config = {"from_attributes": True}
