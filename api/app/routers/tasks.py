"""Task endpoints, including create + move which trigger receipt printing."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, func, select

from .. import events
from ..db import get_session
from ..models import Status, Swimlane, Task, utcnow
from ..schemas import TaskCreate, TaskMove, TaskRead, TaskUpdate
from .boards import get_board_or_404
from .statuses import get_status_or_404
from .swimlanes import get_swimlane_or_404

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_or_404(task_id: int, session: Session) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _next_position(session: Session, board_id: int, swimlane_id: int, status_id: int) -> float:
    current_max = session.exec(
        select(func.max(Task.position)).where(
            Task.board_id == board_id,
            Task.swimlane_id == swimlane_id,
            Task.status_id == status_id,
        )
    ).one()
    return (current_max or 0.0) + 1.0


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)) -> Task:
    return get_task_or_404(task_id, session)


@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    payload: TaskCreate,
    background: BackgroundTasks,
    session: Session = Depends(get_session),
) -> Task:
    board = get_board_or_404(payload.board_id, session)
    lane = get_swimlane_or_404(payload.swimlane_id, session)
    if lane.board_id != board.id:
        raise HTTPException(status_code=400, detail="Swimlane does not belong to this board")

    if payload.status_id is not None:
        status = get_status_or_404(payload.status_id, session)
        if status.board_id != board.id:
            raise HTTPException(status_code=400, detail="Status does not belong to this board")
    else:
        status = session.exec(
            select(Status).where(Status.board_id == board.id).order_by(Status.position, Status.id)
        ).first()
        if not status:
            raise HTTPException(status_code=400, detail="Board has no columns to place the task in")

    task = Task(
        board_id=board.id,
        swimlane_id=lane.id,
        status_id=status.id,
        title=payload.title,
        description=payload.description,
        progress=payload.progress,
        position=_next_position(session, board.id, lane.id, status.id),
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    background.add_task(
        events.on_task_created,
        board=board.name,
        swimlane=lane.name,
        status=status.name,
        title=task.title,
        progress=task.progress,
    )
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)
) -> Task:
    task = get_task_or_404(task_id, session)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    task.updated_at = utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.post("/{task_id}/move", response_model=TaskRead)
def move_task(
    task_id: int,
    payload: TaskMove,
    background: BackgroundTasks,
    session: Session = Depends(get_session),
) -> Task:
    task = get_task_or_404(task_id, session)
    new_status = get_status_or_404(payload.status_id, session)
    if new_status.board_id != task.board_id:
        raise HTTPException(status_code=400, detail="Status does not belong to this task's board")

    old_status = session.get(Status, task.status_id)
    status_changed = new_status.id != task.status_id

    if payload.swimlane_id is not None:
        lane = get_swimlane_or_404(payload.swimlane_id, session)
        if lane.board_id != task.board_id:
            raise HTTPException(status_code=400, detail="Swimlane does not belong to this task's board")
        task.swimlane_id = lane.id

    task.status_id = new_status.id
    task.position = (
        payload.position
        if payload.position is not None
        else _next_position(session, task.board_id, task.swimlane_id, new_status.id)
    )
    # Auto-complete progress when landing in a "Done" column.
    if status_changed and new_status.name.lower() == "done":
        task.progress = 100
    task.updated_at = utcnow()

    lane_name = session.get(Swimlane, task.swimlane_id).name
    session.add(task)
    session.commit()
    session.refresh(task)

    if status_changed:
        background.add_task(
            events.on_task_moved,
            board=get_board_or_404(task.board_id, session).name,
            swimlane=lane_name,
            title=task.title,
            from_status=old_status.name if old_status else "?",
            to_status=new_status.name,
            progress=task.progress,
        )
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)) -> None:
    task = get_task_or_404(task_id, session)
    session.delete(task)
    session.commit()
