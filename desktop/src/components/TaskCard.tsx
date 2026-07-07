import { useDraggable } from "@dnd-kit/core";
import type { Task } from "@taskboard/shared";

export function TaskCard({ task, onOpen }: { task: Task; onOpen: () => void }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: task.id,
  });

  const style = transform
    ? { transform: `translate(${transform.x}px, ${transform.y}px)` }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={"task-card" + (isDragging ? " dragging" : "")}
      {...attributes}
    >
      {/* Drag handle area */}
      <div className="task-drag" {...listeners}>
        <div className="task-title">{task.title}</div>
        <div className="progress">
          <div className="progress-fill" style={{ width: `${task.progress}%` }} />
        </div>
      </div>
      <div className="task-meta">
        <button className="open-task" onClick={onOpen}>
          {task.comments.length > 0 ? `💬 ${task.comments.length}` : "open"}
        </button>
        <span className="progress-label">{task.progress}%</span>
      </div>
    </div>
  );
}
