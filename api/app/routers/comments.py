"""Comment endpoints (nested under a task)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import Comment
from ..schemas import CommentCreate, CommentRead
from .tasks import get_task_or_404

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])


@router.get("", response_model=list[CommentRead])
def list_comments(task_id: int, session: Session = Depends(get_session)) -> list[Comment]:
    get_task_or_404(task_id, session)
    return list(
        session.exec(
            select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at, Comment.id)
        ).all()
    )


@router.post("", response_model=CommentRead, status_code=201)
def create_comment(
    task_id: int, payload: CommentCreate, session: Session = Depends(get_session)
) -> Comment:
    get_task_or_404(task_id, session)
    comment = Comment(task_id=task_id, author=payload.author, body=payload.body)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment
