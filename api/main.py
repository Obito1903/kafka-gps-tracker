from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect
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
from confluent_kafka import Consumer
import asyncio, signal

class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True

class ConnectionManager:
    """Class defining socket events"""
    def __init__(self):
        """init method, keeping track of connections"""
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        """connect event"""
        await websocket.accept()
        self.active_connections.append(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Direct Message"""
        await websocket.send_text(message)

    def disconnect(self, websocket: WebSocket):
        """disconnect event"""
        self.active_connections.remove(websocket)


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


# postregres database -> change to enviroment variable
DATABASE_URL = "postgresql://tracker:tracker@192.168.155.19:5432/tracker"
engine = SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(DATABASE_URL))
database = Database(DATABASE_URL)

api = FastAPI()

manager = ConnectionManager()

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

def get_c():
    try:
        config = {'bootstrap.servers': '192.168.155.19:9094', 'group.id': 'api'}
        c = Consumer(config)
        c.subscribe(['gps'])
        yield c
    finally:
        c.close()

def get_msgs(c):
    while True:
        yield c.poll(1.0)


@api.get("/")
def root():
    return {"hello: world"}


@api.get("/get-gps-data/")
def get_gps_data(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    gps_data = db.query(PostgresData).offset(skip).limit(limit).all()
    return gps_data

@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, consumer: Consumer = Depends(get_c)):
    await manager.connect(websocket)
    try:
        killer = GracefulKiller()
        while not killer.kill_now:
            # await asyncio.sleep(0.1)
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            data = msg.value().decode("utf-8")
            print(data, type(data))
            await websocket.send_text(data)
            # consumer.commit(msg)
            print("sent")
    except WebSocketDisconnect:
        await websocket.close()
    finally:
        consumer.close()
