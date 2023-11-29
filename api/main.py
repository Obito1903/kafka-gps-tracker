from fastapi import FastAPI, WebSocket
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, ConfigDict
from databases import Database
from uuid import uuid4, UUID
from datetime import datetime

Base = declarative_base()

class PostgresData(Base):
    __tablename__ = "gps"

    id = Column(String, primary_key=True, index=True)
    lat = Column(Float)
    lng = Column(Float)
    ip = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    uuid = Column(String)
    client_name = Column(String, nullable=True)


class Location(BaseModel):
    model_config = ConfigDict(title='GPS')
    lat: float
    lng: float
    name: str
    timestamp: int
    uuid: UUID


DATABASE_URL = "postgresql://tracker:tracker@localhost/tracker"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database = Database(DATABASE_URL)

api = FastAPI()


@api.get("/")
def root():
    return {"hello: world"}
