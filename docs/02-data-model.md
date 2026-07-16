# Data model & API reference

## The shape

A **board** is a subject (e.g. "DevOps Certs"). Each board is a set of **swimlanes**, the status
columns. A **task** lives in exactly one swimlane and carries progress and comments.

```
   Pending        In Progress     Complete        ← swimlanes (status columns)
   [task]         [task]          [task]
   [task]         [task]
   [task]
```

Moving a task to a different swimlane is the status change that **prints**.

## Entities

Defined in [`api/app/models.py`](../api/app/models.py) with SQLModel.

| Entity | Key fields | Notes |
| --- | --- | --- |
| **Board** | `id`, `name`, `description`, `position`, `created_at` | A subject. |
| **Swimlane** | `id`, `board_id`, `name`, `position` | A status column. New boards seed `Pending / In Progress / Complete`; fully editable per board. |
| **Task** | `id`, `board_id`, `swimlane_id`, `title`, `description`, `progress` (0–100), `position`, `created_at`, `updated_at` | Lives in one swimlane. |
| **Comment** | `id`, `task_id`, `author`, `body`, `created_at` | Ordered by time. |

**Relationships & deletes.** Every child carries a foreign key with `ON DELETE CASCADE`, and the
SQLite connection enables `PRAGMA foreign_keys=ON` (see [`db.py`](../api/app/db.py)). Deleting a
board removes its swimlanes, tasks, and those tasks' comments; the database handles the ordering, so
the ORM doesn't trip over the cross-references between tasks and their swimlanes.

**Positions** are floats used only for ordering within a list; they are not identity.

**"Done"-style swimlanes.** Moving a task into a swimlane named `Complete`, `Completed`, or `Done`
snaps its `progress` to 100 (see `DONE_NAMES` in `models.py`).

## API

Base URL defaults to `http://127.0.0.1:8000`. Interactive docs are served at `/docs`.

| Method & path | Purpose |
| --- | --- |
| `GET /health` | Liveness + current print mode. |
| `GET /boards` | List board summaries. |
| `POST /boards` | Create a board (seeds default swimlanes). |
| `GET /boards/{id}` | A board with its swimlanes and tasks (comments nested). |
| `PATCH /boards/{id}` · `DELETE /boards/{id}` | Rename/reorder · delete (cascades). |
| `GET/POST /boards/{id}/swimlanes` · `PATCH/DELETE /swimlanes/{id}` | Manage the status columns. |
| `POST /tasks` | Create a task. **Prints a NEW TASK receipt.** |
| `PATCH /tasks/{id}` | Edit title / description / progress. |
| `POST /tasks/{id}/move` | Move to a different swimlane. **Prints a MOVED receipt** when the swimlane changes. |
| `DELETE /tasks/{id}` | Delete a task. |
| `GET/POST /tasks/{id}/comments` | List / add comments. |

### The two side-effecting calls

`POST /tasks`
```json
{ "board_id": 1, "swimlane_id": 3, "title": "Ship the report" }
```
`swimlane_id` is optional; omit it and the task lands in the board's first swimlane.

`POST /tasks/{id}/move`
```json
{ "swimlane_id": 4, "position": 1.5 }
```
Only `swimlane_id` is required. A move into a swimlane named "Complete"/"Done" also sets `progress`
to 100.

## Keeping the contract honest

The response shapes above are declared twice on purpose:

- server-side in [`api/app/schemas.py`](../api/app/schemas.py) (Pydantic),
- client-side in [`packages/shared/src/types.ts`](../packages/shared/src/types.ts) (TypeScript).

They must agree. The TypeScript side is the compile-time guard for both the desktop and mobile apps;
the Pydantic side is the runtime guard at the boundary.
