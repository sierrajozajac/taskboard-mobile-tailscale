"""FastAPI application entrypoint.

Run:  uvicorn app.main:app --reload
Docs: http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import init_db
from .routers import boards, comments, swimlanes, tasks

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
app.include_router(tasks.router)
app.include_router(comments.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "print_mode": settings.print_mode}


# Serve the built board web app (desktop/dist) at "/" so a phone browser can reach
# the UI over Tailscale/LAN at the same address as the API. Mounted last so it only
# catches paths the API routers didn't. Skipped if the build isn't present (e.g. in
# a Docker image or before `npm run build --workspace desktop`).
_WEB_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "desktop", "dist")
)
if os.path.isdir(_WEB_DIST):
    app.mount("/", StaticFiles(directory=_WEB_DIST, html=True), name="web")
    logging.info("Serving board web app from %s", _WEB_DIST)
else:
    logging.info("No web build at %s; API-only.", _WEB_DIST)
