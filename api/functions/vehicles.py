from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api import models, schemas

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.VehicleOut)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = models.Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.get("/{plate}", response_model=list[schemas.VehicleOut])
def search_vehicle(plate: str, db: Session = Depends(get_db)):
    plate_filter = f"%{plate}%"
    records = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.plate.ilike(plate_filter))
        .order_by(models.Vehicle.created_at.desc())
        .all()
    )
    return records
