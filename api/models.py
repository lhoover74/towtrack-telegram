from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    plate = Column(String, index=True)
    plate_state = Column(String)

    vin = Column(String, nullable=True)

    make = Column(String)
    model = Column(String)
    year = Column(String)
    color = Column(String)

    property_name = Column(String)
    location = Column(String)

    tow_reason = Column(String)
    notes = Column(Text)

    status = Column(String, default="Observed")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)