# Printer integration

The signature feature: create or move a task and a receipt slides out of a Rongta RP850. This is
how it works and how to turn it on.

## Reusing what already existed

The RP850 was already driven by a separate project, [`rp850-printer`](../../rp850-printer), which
exposes two useful functions:

- `get_printer(name)`: opens the RP850 as a `python-escpos` `Win32Raw` device via the Windows
  spooler, and
- `build_receipt(...)`: the reference for the 24-character receipt style (centred bold header,
  `=` rules, paper cut).

TaskBoard's API imports `get_printer` directly rather than shelling out or POSTing to that project's
HTTP server. One process, one place that talks to the hardware.

## One formatter, two backends

Everything a receipt needs is the trio `.set()` / `.text()` / `.cut()`. [`printing.py`](../api/app/printing.py)
formats each card against that minimal interface, so the same code drives either:

- **`PRINT_MODE=printer`** → a real `python-escpos` device from `get_printer(PRINTER_NAME)`.
- **`PRINT_MODE=console`** → a `ConsolePrinter` shim that collects the same writes and renders the
  card to the server log, boxed like a paper slip.

That shim is why the whole app is usable with no hardware: you develop and demo in console mode and
flip a single environment variable to print for real.

A console-mode "MOVED" card looks like this:

```
+--------------------------+
| MOVED                    |
| Mon Jul 6 8:07pm         |
| ======================== |
| TASK                     |
|   Verify RP850 over HTTP |
| BOARD                    |
|   DevOps Certs           |
| MOVE                     |
|   Pending -> In Progress |
| PROGRESS                 |
|   [................]  0% |
| ======================== |
+--------------------------+
```

## When it prints

Two events, wired in [`events.py`](../api/app/events.py):

| Event | Endpoint | Card |
| --- | --- | --- |
| Task created | `POST /tasks` | `NEW TASK` |
| Task moved to another swimlane | `POST /tasks/{id}/move` | `MOVED` (or `COMPLETED` when the target swimlane is "Complete"/"Done") |

Editing a task or adding a comment does **not** print; only creation and swimlane moves do.

## Best-effort by design

Printing runs as a FastAPI `BackgroundTask`, after the HTTP response is sent, inside a `try/except`.
So:

- a slow or offline printer never delays or fails an API call;
- a missing driver logs an exception and the task change still stands.

The receipt is a notification about a change that already happened, never a precondition for it.

## Gotcha: finalize every job

`Win32Raw` prints through the Windows spooler: `open()` starts a spool document
(`StartDocPrinter`), writes buffer to it, and **`close()` ends it (`EndDocPrinter`)**, and *ending*
the document is what actually releases the receipt to the paper. A run-once script gets this for
free because the process exits after printing, which finalizes the job. A long-running server does
not: if you open a fresh printer per event and never close it, each receipt sits buffered in the
spooler until some later job flushes it, so moves appear to "pile up" and print several moves late.

The fix is one line of discipline: `printing._emit()` writes each card inside a `try/finally` that
always calls `printer.close()`, so every move finalizes its own job and prints immediately.

## Turning on real printing

1. Install Rongta's Windows driver so the RP850 shows up as a printer.
2. Find its exact name:
   ```bash
   py ../rp850-printer/print_tasks.py --list
   ```
3. In `api/.env`:
   ```ini
   PRINT_MODE=printer
   PRINTER_NAME=POS-80     # whatever --list showed
   PRINT_WIDTH=24          # RP850 default font; recalibrate with print_tasks.py --ruler
   ```
4. Restart the API. `GET /health` will report `"print_mode": "printer"`. Create or move a task and
   watch the paper.

If the API and the `rp850-printer` folder are not siblings, point the API at it with the
`RP850_PATH` environment variable.

## Extending it

New event cards are cheap: add a formatter call in `printing.py` and fire it from the relevant route
via a background task. Candidates worth considering: a daily "board digest" receipt, or printing a
task's comment thread on demand.
