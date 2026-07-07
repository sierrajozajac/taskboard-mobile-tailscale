// Typed API client used by both the desktop and mobile apps.
// Uses the global `fetch` (present in modern browsers, React Native, and Node 18+).

import type {
  Board,
  BoardSummary,
  Comment,
  CreateTaskInput,
  MoveTaskInput,
  Status,
  Swimlane,
  Task,
  UpdateTaskInput,
} from "./types.js";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class TaskBoardClient {
  constructor(private baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(this.baseUrl + path, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        detail = (await res.json())?.detail ?? detail;
      } catch {
        /* non-JSON error body */
      }
      throw new ApiError(res.status, detail);
    }
    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  }

  // Meta
  health() {
    return this.request<{ status: string; print_mode: string }>("/health");
  }

  // Boards
  listBoards() {
    return this.request<BoardSummary[]>("/boards");
  }
  getBoard(id: number) {
    return this.request<Board>(`/boards/${id}`);
  }
  createBoard(name: string, description = "") {
    return this.request<Board>("/boards", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    });
  }
  deleteBoard(id: number) {
    return this.request<void>(`/boards/${id}`, { method: "DELETE" });
  }

  // Swimlanes & statuses
  createSwimlane(boardId: number, name: string) {
    return this.request<Swimlane>(`/boards/${boardId}/swimlanes`, {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  }
  createStatus(boardId: number, name: string) {
    return this.request<Status>(`/boards/${boardId}/statuses`, {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  }

  // Tasks
  createTask(input: CreateTaskInput) {
    return this.request<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(input),
    });
  }
  updateTask(id: number, patch: UpdateTaskInput) {
    return this.request<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    });
  }
  moveTask(id: number, move: MoveTaskInput) {
    return this.request<Task>(`/tasks/${id}/move`, {
      method: "POST",
      body: JSON.stringify(move),
    });
  }
  deleteTask(id: number) {
    return this.request<void>(`/tasks/${id}`, { method: "DELETE" });
  }

  // Comments
  listComments(taskId: number) {
    return this.request<Comment[]>(`/tasks/${taskId}/comments`);
  }
  addComment(taskId: number, body: string, author = "me") {
    return this.request<Comment>(`/tasks/${taskId}/comments`, {
      method: "POST",
      body: JSON.stringify({ body, author }),
    });
  }
}
