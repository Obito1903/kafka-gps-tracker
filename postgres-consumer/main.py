from fastapi import FastAPI
from pydantic import BaseModel

api = FastAPI()




@api.get("/")
def root():
    return {"hello: world"}
