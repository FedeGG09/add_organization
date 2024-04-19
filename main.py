# main.py
from fastapi import FastAPI
from api import organization

app = FastAPI()

app.include_router(organization)
