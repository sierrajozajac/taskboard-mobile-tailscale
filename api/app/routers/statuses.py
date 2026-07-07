"""Status (column) endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import Status
from ..schemas import StatusCreate, StatusRead, StatusUpdate
from .boards import get_board_or_404

router = APIRouter(tags=["statuses"])


def get_status_or_404(status_id: int, session: Session) -> Status:
    status = session.get(Status, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status


@router.get("/boards/{board_id}/statuses", response_model=list[StatusRead])
def list_statuses(board_id: int, session: Session = Depends(get_session)) -> list[Status]:
    get_board_or_404(board_id, session)
    return list(
        session.exec(
            select(Status).where(Status.board_id == board_id).order_by(Status.position, Status.id)
        ).all()
    )


@router.post("/boards/{board_id}/statuses", response_model=StatusRead, status_code=201)
def create_status(
    board_id: int, payload: StatusCreate, session: Session = Depends(get_session)
) -> Status:
    get_board_or_404(board_id, session)
    position = payload.position
    if position is None:
        position = float(len(session.exec(select(Status).where(Status.board_id == board_id)).all()))
    status = Status(board_id=board_id, name=payload.name, position=position)
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@router.patch("/statuses/{status_id}", response_model=StatusRead)
def update_status(
    status_id: int, payload: StatusUpdate, session: Session = Depends(get_session)
) -> Status:
    status = get_status_or_404(status_id, session)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(status, key, value)
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@router.delete("/statuses/{status_id}", status_code=204)
def delete_status(status_id: int, session: Session = Depends(get_session)) -> None:
    status = get_status_or_404(status_id, session)
    session.delete(status)
    session.commit()
