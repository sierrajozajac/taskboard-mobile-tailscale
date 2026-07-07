"""Print triggers. Called as FastAPI BackgroundTasks so printing never blocks or
breaks an API response: a missing driver or offline printer is logged, not raised.

Names (board / swimlane) are resolved up front and passed by value so the
background task doesn't need a live DB session.
"""

from __future__ import annotations

import logging

from . import printing

log = logging.getLogger("taskboard.events")


def on_task_created(*, board: str, swimlane: str, title: str, progress: int) -> None:
    try:
        printing.print_task_created(board=board, swimlane=swimlane, title=title, progress=progress)
    except Exception:  # noqa: BLE001 - printing is best-effort
        log.exception("Failed to print NEW TASK receipt for %r", title)


def on_task_moved(
    *, board: str, title: str, from_swimlane: str, to_swimlane: str, progress: int
) -> None:
    try:
        printing.print_task_moved(
            board=board,
            title=title,
            from_swimlane=from_swimlane,
            to_swimlane=to_swimlane,
            progress=progress,
        )
    except Exception:  # noqa: BLE001 - printing is best-effort
        log.exception("Failed to print MOVED receipt for %r", title)
