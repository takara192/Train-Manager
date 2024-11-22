from contextlib import asynccontextmanager

from fastapi import FastAPI
from prisma import Prisma

db = Prisma()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield

    await db.disconnect()
