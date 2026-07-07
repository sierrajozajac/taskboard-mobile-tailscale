// API contract types. Mirrors api/app/schemas.py — keep the two in sync.

export interface Comment {
  id: number;
  task_id: number;
  author: string;
  body: string;
  created_at: string;
}

export interface Task {
  id: number;
  board_id: number;
  swimlane_id: number;
  title: string;
  description: string;
  progress: number; // 0-100
  position: number;
  created_at: string;
  updated_at: string;
  comments: Comment[];
}

// A swimlane is a status column (Pending, In Progress, Complete, ...).
export interface Swimlane {
  id: number;
  board_id: number;
  name: string;
  position: number;
}

export interface BoardSummary {
  id: number;
  name: string;
  description: string;
  position: number;
  created_at: string;
}

export interface Board extends BoardSummary {
  swimlanes: Swimlane[];
  tasks: Task[];
}

// --- Request payloads ---
export interface CreateTaskInput {
  board_id: number;
  swimlane_id?: number; // defaults to the board's first swimlane
  title: string;
  description?: string;
  progress?: number;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  progress?: number;
}

export interface MoveTaskInput {
  swimlane_id: number;
  position?: number;
}
