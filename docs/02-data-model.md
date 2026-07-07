# Data model & API reference

## The shape

A **board** is a subject (e.g. "DevOps Certs"). Each board is a grid:

- **statuses** are the vertical columns (Backlog → To Do → In Progress → Done),
- **swimlanes** are the horizontal rows (e.g. Study / Labs / Exam Prep),
- a **task** occupies one (swimlane × status) cell and carries progress and comments.

```
                Backlog     To Do     In Progress   Done      ← statuses (columns)
   Study        [task]      [task]    [task]
   Labs                     [task]
   Exam Prep    [task]
   ↑ swimlanes (rows)
```

Moving a task horizontally changes its **status** (and prints). Moving it vertically changes its
**swimlane**.

## Entities

Defined in [`api/app/models.py`](../api/app/models.py) with SQLModel.

| Entity | Key fields | Notes |
| --- | --- | --- |
| **Board** | `id`, `name`, `description`, `position`, `created_at` | A subject. |
| **Status** | `id`, `board_id`, `name`, `position` | A column. Seeded `Backlog/To Do/In Progress/Done`. |
| **Swimlane** | `id`, `board_id`, `name`, `position` | A row. New boards start with one lane, "General". |
| **Task** | `id`, `board_id`, `swimlane_id`, `status_id`, `title`, `description`, `progress` (0–100), `position`, `created_at`, `updated_at` | Lives in one cell. |
| **Comment** | `id`, `task_id`, `author`, `body`, `created_at` | Ordered by time. |

**Relationships & deletes.** Every child carries a foreign key with `ON DELETE CASCADE`, and the
SQLite connection enables `PRAGMA foreign_keys=ON` (see [`db.py`](../api/app/db.py)). Deleting a
board removes its swimlanes, statuses, tasks, and those tasks' comments — the database handles the
ordering, so the ORM doesn't trip over the cross-references between tasks and their lanes/columns.

**Positions** are floats used only for ordering within a list; they are not identity.

## API

Base URL defaults to `http://127.0.0.1:8000`. Interactive docs are served at `/docs`.

| Method & path | Purpose |
| --- | --- |
| `GET /health` | Liveness + current print mode. |
| `GET /boards` | List board summaries. |
| `POST /boards` | Create a board (seeds columns + a lane). |
| `GET /boards/{id}` | A board with its swimlanes, statuses, and tasks (comments nested). |
| `PATCH /boards/{id}` · `DELETE /boards/{id}` | Rename/reorder · delete (cascades). |
| `GET/POST /boards/{id}/swimlanes` · `PATCH/DELETE /swimlanes/{id}` | Manage rows. |
| `GET/POST /boards/{id}/statuses` · `PATCH/DELETE /statuses/{id}` | Manage columns. |
| `POST /tasks` | Create a task. **Prints a NEW TASK receipt.** |
| `PATCH /tasks/{id}` | Edit title / description / progress. |
| `POST /tasks/{id}/move` | Change status (and optionally swimlane). **Prints a MOVED receipt** when the status changes. |
| `DELETE /tasks/{id}` | Delete a task. |
| `GET/POST /tasks/{id}/comments` | List / add comments. |

### The two side-effecting calls

`POST /tasks`
```json
{ "board_id": 1, "swimlane_id": 1, "status_id": 3, "title": "Ship the report" }
```
`status_id` is optional; omit it and the task lands in the board's first column.

`POST /tasks/{id}/move`
```json
{ "status_id": 4, "swimlane_id": 2, "position": 1.5 }
```
Only `status_id` is required. A move into a column named "Done" also sets `progress` to 100.

## Keeping the contract honest

The response shapes above are declared twice on purpose:

- server-side in [`api/app/schemas.py`](../api/app/schemas.py) (Pydantic),
- client-side in [`packages/shared/src/types.ts`](../packages/shared/src/types.ts) (TypeScript).

They must agree. The TypeScript side is the compile-time guard for both the desktop and mobile apps;
the Pydantic side is the runtime guard at the boundary.
