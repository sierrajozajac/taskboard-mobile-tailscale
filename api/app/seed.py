"""Seed demo data so the board is non-empty on first run.

Idempotent-ish: only seeds when there are no boards yet. Run standalone with:
    py -m app.seed
"""

from __future__ import annotations

from sqlmodel import Session, select

from .db import engine, init_db
from .models import Board, Comment, Swimlane, Task

# Each board defines its own swimlanes (status columns) and tasks placed in them.
DEMO = [
    {
        "name": "DevOps Certs",
        "description": "Terraform -> SAA -> DVA -> CKA -> DOP Pro",
        "swimlanes": ["Pending", "In Progress", "Complete"],
        "tasks": [
            ("In Progress", "Terraform: state & backends", 60, ["remote state on S3 next"]),
            ("Pending", "Terraform: modules deep-dive", 0, []),
            ("In Progress", "Build a 2-tier VPC in Terraform", 40, []),
            ("Pending", "Book the Terraform Associate exam", 0, ["aim for October"]),
            ("Complete", "Terraform: providers & resources", 100, []),
        ],
    },
    {
        "name": "Calathea Codex",
        "description": "Substack essays, cuttings, field guides",
        "swimlanes": ["Pending", "Drafting", "In Review", "Published"],
        "tasks": [
            ("Drafting", "Essay: 'The Compost of Old Selves'", 30, ["needs a stronger turn"]),
            ("Pending", "Batch 5 cuttings for the next drop", 0, []),
            ("In Review", "Refresh the About page copy", 70, []),
            ("Published", "Field guide: wiring a thermal printer", 100, []),
        ],
    },
    {
        "name": "Home",
        "description": "Life admin and the printer project",
        "swimlanes": ["Pending", "In Progress", "Complete"],
        "tasks": [
            ("In Progress", "Wire TaskBoard to the RP850", 80, ["prints on move!"]),
            ("In Progress", "Water the calatheas", 50, []),
            ("Pending", "Sell the Notion template ('Unfurl')", 0, []),
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
            board.swimlanes = [Swimlane(name=n, position=i) for i, n in enumerate(spec["swimlanes"])]
            session.add(board)
            session.commit()
            session.refresh(board)

            lanes = {s.name: s for s in board.swimlanes}
            for i, (lane, title, progress, comments) in enumerate(spec["tasks"]):
                task = Task(
                    board_id=board.id,
                    swimlane_id=lanes[lane].id,
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
