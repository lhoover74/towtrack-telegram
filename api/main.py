from fastapi import FastAPI
from .database import Base, engine
from .routes import vehicles

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI
from api.database import Base, engine
from api.functions import vehicles

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TowTrack API")

app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])tapp = FastAPI(title="TowTrack API")

app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
