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
from kafka import KafkaConsumer, TopicPartition
import signal, os, json, time, asyncio, sys

# fetch env variables
POSTGRES_USER: str = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB: str = os.getenv("POSTGRES_DB")
POSTGRES_IP: str = os.getenv("POSTGRES_IP")
KAFKA_IP: str = os.getenv("KAFKA_IP")
KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC") or "gps"

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
    __tablename__ = POSTGRES_DB

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
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_IP}/{POSTGRES_DB}"
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

consumer = KafkaConsumer(bootstrap_servers=KAFKA_IP, api_version=(0, 0, 0), group_id="yes", enable_auto_commit=True, auto_offset_reset='earliest', value_deserializer=lambda x: json.loads(x.decode('utf-8')), consumer_timeout_ms=500)
partition = TopicPartition(KAFKA_TOPIC, 0)
consumer.assign([partition])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        print("Websocket Connected", file=sys.stderr)
        while True:
            print("Fetching..", file=sys.stderr)
            end_offset = consumer.end_offsets([partition])
            consumer.seek(partition, list(end_offset.values())[0])
            for msg in consumer:
                print("sending..", file=sys.stderr)
                await websocket.send_text(json.dumps(msg.value))
                print(msg.value, file=sys.stderr)
        print("Websocket End", file=sys.stderr)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
