import { useEffect, useState } from "react";
import type { Board, Task } from "@taskboard/shared";
import { makeClient } from "../api";

interface Props {
  task: Task;
  board: Board;
  onClose: () => void;
  onChanged: (task: Task) => void;
  onDeleted: () => void;
}

export function TaskDrawer({ task, board, onClose, onChanged, onDeleted }: Props) {
  const [description, setDescription] = useState(task.description);
  const [progress, setProgress] = useState(task.progress);
  const [comment, setComment] = useState("");

  useEffect(() => {
    setDescription(task.description);
    setProgress(task.progress);
  }, [task.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const laneName = board.swimlanes.find((l) => l.id === task.swimlane_id)?.name ?? "";
  const statusName = board.statuses.find((s) => s.id === task.status_id)?.name ?? "";

  async function saveField(patch: Partial<Pick<Task, "description" | "progress">>) {
    const updated = await makeClient().updateTask(task.id, patch);
    onChanged(updated);
  }

  async function addComment() {
    if (!comment.trim()) return;
    await makeClient().addComment(task.id, comment.trim());
    setComment("");
    onChanged(await makeClient().getBoard(board.id).then((b) => b.tasks.find((t) => t.id === task.id)!));
  }

  async function remove() {
    if (!confirm("Delete this task?")) return;
    await makeClient().deleteTask(task.id);
    onDeleted();
  }

  return (
    <div className="drawer">
      <div className="drawer-head">
        <div>
          <div className="chip">{laneName} · {statusName}</div>
          <h2>{task.title}</h2>
        </div>
        <button className="icon-btn" onClick={onClose}>
          ✕
        </button>
      </div>

      <label className="field-label">Description</label>
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        onBlur={() => description !== task.description && saveField({ description })}
        rows={4}
        placeholder="Add a description…"
      />

      <label className="field-label">Progress: {progress}%</label>
      <input
        type="range"
        min={0}
        max={100}
        value={progress}
        onChange={(e) => setProgress(Number(e.target.value))}
        onMouseUp={() => progress !== task.progress && saveField({ progress })}
      />

      <label className="field-label">Comments ({task.comments.length})</label>
      <div className="comments">
        {task.comments.map((c) => (
          <div key={c.id} className="comment">
            <div className="comment-author">{c.author}</div>
            <div className="comment-body">{c.body}</div>
          </div>
        ))}
        {task.comments.length === 0 && <div className="muted">No comments yet.</div>}
      </div>
      <div className="comment-add">
        <input
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addComment()}
          placeholder="Write a comment…"
        />
        <button onClick={addComment}>Add</button>
      </div>

      <button className="danger" onClick={remove}>
        Delete task
      </button>
    </div>
  );
}
