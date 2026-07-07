import { useDroppable } from "@dnd-kit/core";
import type { Board, Swimlane } from "@taskboard/shared";
import { TaskCard } from "./TaskCard";

interface Props {
  board: Board;
  onOpenTask: (id: number) => void;
  onAddTask: (swimlaneId: number) => void;
}

export function BoardView({ board, onOpenTask, onAddTask }: Props) {
  const swimlanes = [...board.swimlanes].sort((a, b) => a.position - b.position);

  return (
    <div className="board">
      <header className="board-header">
        <h1>{board.name}</h1>
        {board.description && <p>{board.description}</p>}
      </header>

      <div className="lanes">
        {swimlanes.map((lane) => (
          <SwimlaneColumn
            key={lane.id}
            lane={lane}
            board={board}
            onOpenTask={onOpenTask}
            onAddTask={onAddTask}
          />
        ))}
      </div>
    </div>
  );
}

function SwimlaneColumn({
  lane,
  board,
  onOpenTask,
  onAddTask,
}: {
  lane: Swimlane;
  board: Board;
  onOpenTask: (id: number) => void;
  onAddTask: (swimlaneId: number) => void;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: lane.id });
  const tasks = board.tasks
    .filter((t) => t.swimlane_id === lane.id)
    .sort((a, b) => a.position - b.position);

  return (
    <div className={"lane" + (isOver ? " over" : "")} ref={setNodeRef}>
      <div className="lane-header">
        <span className="lane-name">{lane.name}</span>
        <span className="lane-count">{tasks.length}</span>
      </div>
      <div className="lane-body">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} onOpen={() => onOpenTask(task.id)} />
        ))}
      </div>
      <button className="add-task" onClick={() => onAddTask(lane.id)}>
        + Add task
      </button>
    </div>
  );
}
