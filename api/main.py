from fastapi import FastAPI, WebSocket
from pydantic import BaseModel, ConfigDict
from uuid import uuid4, UUID

api = FastAPI()

class gps(BaseModel):
    model_config = ConfigDict(title='GPS')
    lat: float
    lng: float
    name: str
    datetime: str
    uuid: UUID


@api.get("/")
def root():
    return {"hello: world"}
