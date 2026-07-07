"""Seed demo data so the board is non-empty on first run.

Idempotent-ish: only seeds when there are no boards yet. Run standalone with:
    py -m app.seed
"""

from __future__ import annotations

from sqlmodel import Session, select

from .db import engine, init_db
from .models import DEFAULT_STATUSES, Board, Comment, Status, Swimlane, Task

# (board, description, [swimlanes], [(swimlane, status, title, progress, [comments])])
DEMO = [
    {
        "name": "DevOps Certs",
        "description": "Terraform -> SAA -> DVA -> CKA -> DOP Pro",
        "swimlanes": ["Study", "Labs", "Exam Prep"],
        "tasks": [
            ("Study", "In Progress", "Terraform: state & backends", 60, ["remote state on S3 next"]),
            ("Study", "To Do", "Terraform: modules deep-dive", 0, []),
            ("Labs", "In Progress", "Build a 2-tier VPC in Terraform", 40, []),
            ("Exam Prep", "Backlog", "Book Terraform Associate exam", 0, ["aim for October"]),
            ("Study", "Done", "Terraform: providers & resources", 100, []),
        ],
    },
    {
        "name": "Calathea Codex",
        "description": "Substack essays, cuttings, field guides",
        "swimlanes": ["Essays", "Cuttings", "Admin"],
        "tasks": [
            ("Essays", "In Progress", "Draft: 'The Compost of Old Selves'", 30, ["needs a stronger turn"]),
            ("Cuttings", "To Do", "Batch 5 cuttings for the next drop", 0, []),
            ("Admin", "Backlog", "Refresh the About page copy", 0, []),
        ],
    },
    {
        "name": "Home",
        "description": "Life admin and the printer project",
        "swimlanes": ["This Week", "Someday"],
        "tasks": [
            ("This Week", "To Do", "Wire TaskBoard to the RP850", 20, ["console mode works!"]),
            ("This Week", "In Progress", "Water the calatheas", 50, []),
            ("Someday", "Backlog", "Sell the Notion template ('Unfurl')", 0, []),
        ],
    },
]


def seed() -> None:
    init_db()
    with Session(engine) as session:
        if session.exec(select(Board)).first():
            print("Database already has boards; skipping seed.")
            return

        for pos, spec in enumerate(DEMO):
            board = Board(name=spec["name"], description=spec["description"], position=pos)
            board.statuses = [Status(name=n, position=i) for i, n in enumerate(DEFAULT_STATUSES)]
            board.swimlanes = [Swimlane(name=n, position=i) for i, n in enumerate(spec["swimlanes"])]
            session.add(board)
            session.commit()
            session.refresh(board)

            lanes = {s.name: s for s in board.swimlanes}
            cols = {s.name: s for s in board.statuses}
            for i, (lane, status, title, progress, comments) in enumerate(spec["tasks"]):
                task = Task(
                    board_id=board.id,
                    swimlane_id=lanes[lane].id,
                    status_id=cols[status].id,
                    title=title,
                    progress=progress,
                    position=i,
                )
                task.comments = [Comment(body=b) for b in comments]
                session.add(task)
            session.commit()
        print(f"Seeded {len(DEMO)} boards.")


if __name__ == "__main__":
    seed()
