"""Board (subject) endpoints. Creating a board seeds its default columns and one lane."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import DEFAULT_SWIMLANES, Board, Swimlane
from ..schemas import BoardCreate, BoardRead, BoardSummary, BoardUpdate

router = APIRouter(prefix="/boards", tags=["boards"])


def get_board_or_404(board_id: int, session: Session) -> Board:
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.get("", response_model=list[BoardSummary])
def list_boards(session: Session = Depends(get_session)) -> list[Board]:
    return list(session.exec(select(Board).order_by(Board.position, Board.id)).all())


@router.post("", response_model=BoardRead, status_code=201)
def create_board(payload: BoardCreate, session: Session = Depends(get_session)) -> Board:
    count = len(session.exec(select(Board.id)).all())
    board = Board(name=payload.name, description=payload.description, position=count)
    # Seed the default status columns (swimlanes).
    board.swimlanes = [Swimlane(name=name, position=i) for i, name in enumerate(DEFAULT_SWIMLANES)]
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


@router.get("/{board_id}", response_model=BoardRead)
def get_board(board_id: int, session: Session = Depends(get_session)) -> Board:
    return get_board_or_404(board_id, session)


@router.patch("/{board_id}", response_model=BoardRead)
def update_board(
    board_id: int, payload: BoardUpdate, session: Session = Depends(get_session)
) -> Board:
    board = get_board_or_404(board_id, session)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(board, key, value)
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


@router.delete("/{board_id}", status_code=204)
def delete_board(board_id: int, session: Session = Depends(get_session)) -> None:
    board = get_board_or_404(board_id, session)
    session.delete(board)
    session.commit()
