"""Swimlane (row) endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import Swimlane
from ..schemas import SwimlaneCreate, SwimlaneRead, SwimlaneUpdate
from .boards import get_board_or_404

router = APIRouter(tags=["swimlanes"])


def get_swimlane_or_404(swimlane_id: int, session: Session) -> Swimlane:
    lane = session.get(Swimlane, swimlane_id)
    if not lane:
        raise HTTPException(status_code=404, detail="Swimlane not found")
    return lane


@router.get("/boards/{board_id}/swimlanes", response_model=list[SwimlaneRead], tags=["swimlanes"])
def list_swimlanes(board_id: int, session: Session = Depends(get_session)) -> list[Swimlane]:
    get_board_or_404(board_id, session)
    return list(
        session.exec(
            select(Swimlane).where(Swimlane.board_id == board_id).order_by(Swimlane.position, Swimlane.id)
        ).all()
    )


@router.post("/boards/{board_id}/swimlanes", response_model=SwimlaneRead, status_code=201)
def create_swimlane(
    board_id: int, payload: SwimlaneCreate, session: Session = Depends(get_session)
) -> Swimlane:
    get_board_or_404(board_id, session)
    position = payload.position
    if position is None:
        position = float(len(session.exec(select(Swimlane).where(Swimlane.board_id == board_id)).all()))
    lane = Swimlane(board_id=board_id, name=payload.name, position=position)
    session.add(lane)
    session.commit()
    session.refresh(lane)
    return lane


@router.patch("/swimlanes/{swimlane_id}", response_model=SwimlaneRead)
def update_swimlane(
    swimlane_id: int, payload: SwimlaneUpdate, session: Session = Depends(get_session)
) -> Swimlane:
    lane = get_swimlane_or_404(swimlane_id, session)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lane, key, value)
    session.add(lane)
    session.commit()
    session.refresh(lane)
    return lane


@router.delete("/swimlanes/{swimlane_id}", status_code=204)
def delete_swimlane(swimlane_id: int, session: Session = Depends(get_session)) -> None:
    lane = get_swimlane_or_404(swimlane_id, session)
    session.delete(lane)
    session.commit()
