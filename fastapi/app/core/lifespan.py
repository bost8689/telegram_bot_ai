# app/lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.session import AsyncSessionLocal
from app.core.config import settings
from pydantic import BaseModel, Field
import asyncio
from app.core.logging import get_logger
logger = get_logger("lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('lifespan')
    yield
   