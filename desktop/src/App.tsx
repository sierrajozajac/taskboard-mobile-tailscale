import { useCallback, useEffect, useState } from "react";
import {
  DndContext,
  DragEndEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import type { Board, BoardSummary, Task } from "@taskboard/shared";
import { makeClient } from "./api";
import { Sidebar } from "./components/Sidebar";
import { BoardView } from "./components/BoardView";
import { TaskDrawer } from "./components/TaskDrawer";

export function App() {
  const [boards, setBoards] = useState<BoardSummary[]>([]);
  const [boardId, setBoardId] = useState<number | null>(null);
  const [board, setBoard] = useState<Board | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
  );

  const loadBoards = useCallback(async () => {
    try {
      const list = await makeClient().listBoards();
      setBoards(list);
      setError(null);
      if (list.length && boardId === null) setBoardId(list[0].id);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [boardId]);

  const loadBoard = useCallback(async (id: number) => {
    try {
      setBoard(await makeClient().getBoard(id));
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  useEffect(() => {
    loadBoards();
  }, [loadBoards]);

  useEffect(() => {
    if (boardId !== null) loadBoard(boardId);
  }, [boardId, loadBoard]);

  const refresh = useCallback(() => {
    if (boardId !== null) loadBoard(boardId);
  }, [boardId, loadBoard]);

  async function handleCreateBoard() {
    const name = prompt("New board (subject) name:");
    if (!name) return;
    const created = await makeClient().createBoard(name);
    await loadBoards();
    setBoardId(created.id);
  }

  async function handleCreateTask(swimlaneId: number) {
    const title = prompt("New task title:");
    if (!title || boardId === null) return;
    await makeClient().createTask({
      board_id: boardId,
      swimlane_id: swimlaneId,
      title,
    });
    refresh();
  }

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over) return;
    const taskId = Number(active.id);
    const swimlaneId = Number(over.id);
    const task = board?.tasks.find((t) => t.id === taskId);
    if (!task || task.swimlane_id === swimlaneId) return;
    // Optimistic move, then persist (persisting triggers the printer).
    setBoard((b) =>
      b
        ? {
            ...b,
            tasks: b.tasks.map((t) =>
              t.id === taskId ? { ...t, swimlane_id: swimlaneId } : t,
            ),
          }
        : b,
    );
    try {
      await makeClient().moveTask(taskId, { swimlane_id: swimlaneId });
    } finally {
      refresh();
    }
  }

  function handleTaskChanged(updated: Task) {
    setBoard((b) =>
      b ? { ...b, tasks: b.tasks.map((t) => (t.id === updated.id ? updated : t)) } : b,
    );
  }

  const selectedTask = board?.tasks.find((t) => t.id === selectedTaskId) ?? null;

  return (
    <div className="app">
      <Sidebar
        boards={boards}
        activeId={boardId}
        onSelect={setBoardId}
        onCreate={handleCreateBoard}
        onSettingsChanged={() => {
          loadBoards();
          refresh();
        }}
      />
      <main className="main">
        {error && <div className="banner error">API error: {error}</div>}
        <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
          {board ? (
            <BoardView
              board={board}
              onOpenTask={setSelectedTaskId}
              onAddTask={handleCreateTask}
            />
          ) : (
            <div className="empty">
              {boards.length ? "Select a board." : "No boards yet — create one."}
            </div>
          )}
        </DndContext>
      </main>
      {selectedTask && (
        <TaskDrawer
          task={selectedTask}
          board={board!}
          onClose={() => setSelectedTaskId(null)}
          onChanged={handleTaskChanged}
          onDeleted={() => {
            setSelectedTaskId(null);
            refresh();
          }}
        />
      )}
    </div>
  );
}
