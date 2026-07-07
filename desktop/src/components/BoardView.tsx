import { useDroppable } from "@dnd-kit/core";
import type { Board, Status, Swimlane } from "@taskboard/shared";
import { TaskCard } from "./TaskCard";

interface Props {
  board: Board;
  onOpenTask: (id: number) => void;
  onAddTask: (swimlaneId: number, statusId: number) => void;
}

export function BoardView({ board, onOpenTask, onAddTask }: Props) {
  const statuses = [...board.statuses].sort((a, b) => a.position - b.position);
  const swimlanes = [...board.swimlanes].sort((a, b) => a.position - b.position);

  return (
    <div className="board">
      <header className="board-header">
        <h1>{board.name}</h1>
        {board.description && <p>{board.description}</p>}
      </header>

      <div
        className="grid"
        style={{ gridTemplateColumns: `160px repeat(${statuses.length}, minmax(200px, 1fr))` }}
      >
        <div className="grid-corner" />
        {statuses.map((s) => (
          <div key={s.id} className="col-head">
            {s.name}
          </div>
        ))}

        {swimlanes.map((lane) => (
          <LaneRow
            key={lane.id}
            lane={lane}
            statuses={statuses}
            board={board}
            onOpenTask={onOpenTask}
            onAddTask={onAddTask}
          />
        ))}
      </div>
    </div>
  );
}

function LaneRow({
  lane,
  statuses,
  board,
  onOpenTask,
  onAddTask,
}: {
  lane: Swimlane;
  statuses: Status[];
  board: Board;
  onOpenTask: (id: number) => void;
  onAddTask: (swimlaneId: number, statusId: number) => void;
}) {
  return (
    <>
      <div className="lane-head">{lane.name}</div>
      {statuses.map((status) => (
        <Cell
          key={status.id}
          lane={lane}
          status={status}
          board={board}
          onOpenTask={onOpenTask}
          onAddTask={onAddTask}
        />
      ))}
    </>
  );
}

function Cell({
  lane,
  status,
  board,
  onOpenTask,
  onAddTask,
}: {
  lane: Swimlane;
  status: Status;
  board: Board;
  onOpenTask: (id: number) => void;
  onAddTask: (swimlaneId: number, statusId: number) => void;
}) {
  const id = `${lane.id}:${status.id}`;
  const { setNodeRef, isOver } = useDroppable({ id });
  const tasks = board.tasks
    .filter((t) => t.swimlane_id === lane.id && t.status_id === status.id)
    .sort((a, b) => a.position - b.position);

  return (
    <div ref={setNodeRef} className={"cell" + (isOver ? " over" : "")}>
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} onOpen={() => onOpenTask(task.id)} />
      ))}
      <button className="add-task" onClick={() => onAddTask(lane.id, status.id)}>
        +
      </button>
    </div>
  );
}
