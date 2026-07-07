"""SQLModel tables for TaskBoard.

The shape is a Kanban grid per board (subject):
  Board 1--* Swimlane   (horizontal rows)
  Board 1--* Status     (vertical columns)
  Board 1--* Task       (a task sits at one swimlane x status cell)
  Task  1--* Comment

Deleting a board cascades to its swimlanes, statuses, tasks, and their comments.

Note: no `from __future__ import annotations` here — SQLModel resolves relationship
targets from the raw annotations, and stringized generics (list['Swimlane']) break it.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Default columns seeded for every new board.
DEFAULT_STATUSES = ["Backlog", "To Do", "In Progress", "Done"]


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
    statuses: list["Status"] = Relationship(
        back_populates="board",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "Status.position",
            "passive_deletes": True,
        },
    )
    tasks: list["Task"] = Relationship(
        back_populates="board",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )


class Swimlane(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True, ondelete="CASCADE")
    name: str
    position: float = 0.0

    board: Optional[Board] = Relationship(back_populates="swimlanes")


class Status(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True, ondelete="CASCADE")
    name: str
    position: float = 0.0

    board: Optional[Board] = Relationship(back_populates="statuses")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True, ondelete="CASCADE")
    swimlane_id: int = Field(foreign_key="swimlane.id", index=True, ondelete="CASCADE")
    status_id: int = Field(foreign_key="status.id", index=True, ondelete="CASCADE")
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
