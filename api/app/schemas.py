"""Request/response DTOs. Kept separate from the ORM tables so the API contract
is explicit (and matches packages/shared/src/types.ts on the client side)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Boards ---
class BoardCreate(BaseModel):
    name: str
    description: str = ""


class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    position: Optional[float] = None


# --- Swimlanes (status columns) ---
class SwimlaneCreate(BaseModel):
    name: str
    position: Optional[float] = None


class SwimlaneUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[float] = None


# --- Tasks ---
class TaskCreate(BaseModel):
    board_id: int
    swimlane_id: Optional[int] = None  # defaults to the board's first swimlane
    title: str
    description: str = ""
    progress: int = Field(default=0, ge=0, le=100)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)


class TaskMove(BaseModel):
    swimlane_id: int
    position: Optional[float] = None


# --- Comments ---
class CommentCreate(BaseModel):
    body: str
    author: str = "me"


# --- Read models (responses) ---
class CommentRead(BaseModel):
    id: int
    task_id: int
    author: str
    body: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskRead(BaseModel):
    id: int
    board_id: int
    swimlane_id: int
    title: str
    description: str
    progress: int
    position: float
    created_at: datetime
    updated_at: datetime
    comments: list[CommentRead] = []

    class Config:
        from_attributes = True


class SwimlaneRead(BaseModel):
    id: int
    board_id: int
    name: str
    position: float

    class Config:
        from_attributes = True


class BoardSummary(BaseModel):
    id: int
    name: str
    description: str
    position: float
    created_at: datetime

    class Config:
        from_attributes = True


class BoardRead(BoardSummary):
    swimlanes: list[SwimlaneRead] = []
    tasks: list[TaskRead] = []
