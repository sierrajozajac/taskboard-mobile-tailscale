"""SQLModel tables for TaskBoard.

The shape is a simple Kanban board per subject:
  Board 1--* Swimlane   (the status columns: Pending, In Progress, Complete, ...)
  Board 1--* Task       (a task lives in exactly one swimlane)
  Task  1--* Comment

Moving a task to a different swimlane is the "status change" that prints a receipt.
Deleting a board cascades to its swimlanes, tasks, and their comments.

Note: no `from __future__ import annotations` here — SQLModel resolves relationship
targets from the raw annotations, and stringized generics (list['Swimlane']) break it.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Default swimlanes (status columns) seeded for every new board.
DEFAULT_SWIMLANES = ["Pending", "In Progress", "Complete"]

# Swimlane names that mean "finished" — landing here snaps a task to 100%.
DONE_NAMES = {"complete", "completed", "done"}


class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    position: float = 0.0
    created_at: datetime = Field(default_factory=utcnow)

    # passive_deletes lets the DB's ON DELETE CASCADE (below) handle child removal
    # in the correct FK order, instead of the ORM deleting rows one-by-one.
    swimlanes: list["Swimlane"] = Relationship(
        back_populates="board",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "Swimlane.position",
            "passive_deletes": True,
        },
    )
    tasks: list["Task"] = Relationship(
        back_populates="board",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )


class Swimlane(SQLModel, table=True):
    """A status column on a board (e.g. Pending / In Progress / Complete)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True, ondelete="CASCADE")
    name: str
    position: float = 0.0

    board: Optional[Board] = Relationship(back_populates="swimlanes")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True, ondelete="CASCADE")
    swimlane_id: int = Field(foreign_key="swimlane.id", index=True, ondelete="CASCADE")
    title: str
    description: str = ""
    progress: int = 0  # 0-100
    position: float = 0.0
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    board: Optional[Board] = Relationship(back_populates="tasks")
    comments: list["Comment"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "Comment.created_at",
            "passive_deletes": True,
        },
    )


class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id", index=True, ondelete="CASCADE")
    author: str = "me"
    body: str
    created_at: datetime = Field(default_factory=utcnow)

    task: Optional[Task] = Relationship(back_populates="comments")
