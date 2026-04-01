from pydantic import BaseModel
from typing import Optional


class VehicleCreate(BaseModel):
    plate: str
    property_name: str
    location: str
    tow_reason: str
    notes: Optional[str] = None


class VehicleOut(BaseModel):
    id: int
    plate: str
    property_name: str
    location: str
    tow_reason: str
    status: str

    class Config:
        from_attributes = True