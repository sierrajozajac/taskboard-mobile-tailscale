"""FastAPI application entrypoint.

Run:  uvicorn app.main:app --reload
Docs: http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routers import boards, comments, statuses, swimlanes, tasks

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="TaskBoard API",
    version="0.1.0",
    description="Subjects, swimlanes, tasks, comments — and receipts on the RP850.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(boards.router)
app.include_router(swimlanes.router)
app.include_router(statuses.router)
app.include_router(tasks.router)
app.include_router(comments.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "print_mode": settings.print_mode}
