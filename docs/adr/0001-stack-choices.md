# ADR 0001 — Stack choices

- **Status:** Accepted
- **Date:** 2026-07-06
- **Context:** Greenfield portfolio project — a receipt-printing Kanban board with a desktop app, a
  mobile app, and a database, integrating an existing Python printer script.

## Decision

| Layer | Choice | Alternatives considered |
| --- | --- | --- |
| Backend | **FastAPI + SQLModel** | Node/Express, Django |
| Database | **SQLite** | Postgres (Docker) |
| Shared code | **One TypeScript package** (types + client) | Duplicate types per app; OpenAPI codegen |
| Desktop | **Tauri (Rust shell) + React** | Electron |
| Mobile | **Expo / React Native** | Flutter, PWA |

## Why

**FastAPI + SQLite.** The printer is Python and lives on one PC, so a Python backend can import the
existing `rp850-printer` code directly — no second process, no HTTP hop to the hardware. The data is
small, local, and single-writer, which is exactly SQLite's sweet spot: zero infrastructure, a file
you can copy or delete. SQLModel gives typed models and Pydantic schemas from one definition.

**One TypeScript package for the contract.** Desktop and mobile are both React/TypeScript, so the
response types and a `fetch` client live once in `packages/shared` and are imported by both. Hand-
written (rather than OpenAPI-generated) types keep the toolchain trivial for a project this size; the
cost is discipline — the types must be kept in step with the Pydantic schemas, and CI typechecks
both clients against them.

**Tauri over Electron.** Smaller binaries, lower memory, a modern Rust shell — and a stronger
portfolio signal — while still wrapping an ordinary React app. The React UI runs in a plain browser
during development, so day-to-day work needs no Rust at all; Rust is only required to produce the
native window.

**Expo / React Native over Flutter or a PWA.** Expo shares the language, the types, and the API
client with the desktop app: one skill set, maximum reuse. Flutter would mean a second language
(Dart) and a duplicated client; a PWA would be the least work but the weakest "real mobile app"
story.

## Consequences

- **Two prerequisites are heavier than the rest.** Tauri needs the Rust toolchain and the MSVC C++
  build tools on Windows. The backend and mobile app have no such requirement, so the project is
  fully usable before those are installed.
- **The API must run where the printer is.** Real printing requires the backend on the PC with the
  RP850; other machines and phones are clients over the LAN. The Dockerfile therefore defaults to
  `PRINT_MODE=console`.
- **The contract is enforced by convention + CI**, not generated. If the two type definitions drift,
  a client typecheck should catch it — a future project could replace this with schema-driven codegen.

## Revisit if…

- the data outgrows a single writer or needs multi-device sync → move to Postgres and a hosted API;
- the hand-maintained types become a source of bugs → generate the client from the OpenAPI schema
  FastAPI already produces.
