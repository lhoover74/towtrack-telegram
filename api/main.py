from fastapi import FastAPI
from api.database import Base, engine
from api.functions import vehicles

app = FastAPI(title="TowTrack API")

Base.metadata.create_all(bind=engine)

app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
