from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    roles: List[str] = []
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = {"from_attributes": True}
