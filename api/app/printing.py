"""Bridge to the RP850 thermal printer.

Reuses Sierra's existing rp850-printer code: `get_printer()` opens the RP850 as a
python-escpos Win32Raw device, and we format task-event cards in the same 24-char
receipt style as `build_receipt()`.

Two modes (config PRINT_MODE):
  * "printer" -> a real escpos device via get_printer(PRINTER_NAME)
  * "console" -> a ConsolePrinter shim that renders the same card to stdout,
                 so the whole app is usable with no hardware attached.

Both modes drive the same `_card()` writer through a tiny printer interface
(.set / .text / .cut), so there is exactly one formatter to maintain.
"""

from __future__ import annotations

import os
import sys
import textwrap
from datetime import datetime

from .config import settings


def _rp850_dir() -> str:
    """Path to the sibling rp850-printer project (override with RP850_PATH)."""
    override = os.environ.get("RP850_PATH")
    if override:
        return override
    here = os.path.dirname(os.path.abspath(__file__))
    # app -> api -> taskboard -> <parent>/rp850-printer
    return os.path.abspath(os.path.join(here, os.pardir, os.pardir, os.pardir, "rp850-printer"))


class ConsolePrinter:
    """A no-hardware stand-in with the subset of the escpos API we use."""

    def __init__(self) -> None:
        self._lines: list[str] = []

    def set(self, **_kwargs) -> None:  # formatting is ignored in console mode
        pass

    def text(self, s: str) -> None:
        self._lines.append(s)

    def cut(self) -> None:
        body = "".join(self._lines).rstrip("\n")
        border = "+" + "-" * (settings.print_width + 2) + "+"
        print("\n[print] ---- RP850 receipt (console mode) ----", file=sys.stderr)
        print(border, file=sys.stderr)
        for line in body.split("\n"):
            print(f"| {line:<{settings.print_width}} |", file=sys.stderr)
        print(border + "\n", file=sys.stderr)
        self._lines.clear()

    def close(self) -> None:  # parity with the escpos printer interface
        pass


def _open_printer():
    """Return an object exposing .set/.text/.cut for the active PRINT_MODE."""
    if settings.print_mode == "printer":
        sys.path.insert(0, _rp850_dir())
        from print_tasks import get_printer  # type: ignore

        return get_printer(settings.printer_name)
    return ConsolePrinter()


def _wrap(text: str, indent: str = "  ") -> str:
    return textwrap.fill(
        text.strip(),
        width=settings.print_width,
        initial_indent=indent,
        subsequent_indent=indent,
    )


def _card(printer, *, kind: str, lines: list[tuple[str, str]]) -> None:
    """Write a titled event card. `lines` is a list of (label, value) pairs."""
    width = settings.print_width
    now = datetime.now()

    printer.set(align="center", bold=True, double_height=True, double_width=True)
    printer.text(kind + "\n")
    printer.set(align="center", bold=False, double_height=False, double_width=False)
    printer.text(now.strftime("%a %b ").rstrip() + f" {now.day} " + now.strftime("%I:%M%p").lstrip("0").lower() + "\n")
    printer.text("=" * width + "\n")

    printer.set(align="left")
    for label, value in lines:
        printer.set(bold=True)
        printer.text(label + "\n")
        printer.set(bold=False)
        printer.text(_wrap(value) + "\n")

    printer.text("=" * width + "\n")
    printer.text("\n")
    printer.cut()


def _progress_bar(progress: int) -> str:
    # Leaves room for the 2-char indent _wrap adds, plus "[]" and " 100%".
    slots = max(1, settings.print_width - 8)
    filled = round(slots * max(0, min(100, progress)) / 100)
    return "[" + "#" * filled + "." * (slots - filled) + f"]{progress:>3}%"


def _emit(kind: str, lines: list[tuple[str, str]]) -> None:
    """Open the printer, write one card, and always close the job.

    close() is what finalizes the Windows spool document (EndDocPrinter). Without
    it the receipt sits buffered until a later job flushes it — the reason moves
    appeared to "pile up" and print several moves late.
    """
    printer = _open_printer()
    try:
        _card(printer, kind=kind, lines=lines)
    finally:
        printer.close()


def print_task_created(*, board: str, swimlane: str, title: str, progress: int) -> None:
    _emit(
        "NEW TASK",
        [
            ("TASK", title),
            ("BOARD", board),
            ("SWIMLANE", swimlane),
        ],
    )


def print_task_moved(
    *, board: str, title: str, from_swimlane: str, to_swimlane: str, progress: int
) -> None:
    kind = "COMPLETED" if to_swimlane.strip().lower() in {"complete", "completed", "done"} else "MOVED"
    _emit(
        kind,
        [
            ("TASK", title),
            ("BOARD", board),
            ("MOVE", f"{from_swimlane} -> {to_swimlane}"),
            ("PROGRESS", _progress_bar(progress)),
        ],
    )
