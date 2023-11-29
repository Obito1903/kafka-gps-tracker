from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, ConfigDict
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from databases import Database
from uuid import uuid4, UUID
from datetime import datetime

Base = declarative_base()

class PostgresData(Base):
    __tablename__ = "position"

    lat = Column(Float)
    lng = Column(Float)
    timestamp = Column(Integer)
    uuid = Column(String, primary_key=True)
    name = Column(String)


class Location(BaseModel):
    model_config = ConfigDict(title='GPS')
    lat: float
    lng: float
    name: str
    timestamp: int
    uuid: UUID


DATABASE_URL = "postgresql://tracker:tracker@192.168.155.19:5432/tracker"
engine = SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(DATABASE_URL))
database = Database(DATABASE_URL)

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@api.get("/")
def root():
    return {"hello: world"}


@api.get("/get-gps-data/")
def get_gps_data(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    gps_data = db.query(PostgresData).offset(skip).limit(limit).all()
    return gps_data
