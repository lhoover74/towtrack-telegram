from pydantic import BaseModel
from typing import Optional


class VehicleCreate(BaseModel):
    plate: str
    property_name: str
    location: str
    tow_reason: str
    notes: Optional[str] = None


from datetime import datetime


class VehicleOut(BaseModel):
    id: int
    plate: str
    property_name: str
    location: str
    tow_reason: str
    notes: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True