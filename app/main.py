from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles          
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.routers import customers
from app.util.settings import settings
from app.routers import ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # startup
    yield                                   # app runs
    # (no shutdown logic yet)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to the Customer API"}

@app.get("/status")
def status() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(customers.router)
app.include_router(ai.router) 

