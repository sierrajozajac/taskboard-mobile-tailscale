import { useState } from "react";
import type { BoardSummary } from "@taskboard/shared";
import { getApiUrl, setApiUrl } from "../api";

interface Props {
  boards: BoardSummary[];
  activeId: number | null;
  open: boolean;
  onSelect: (id: number) => void;
  onCreate: () => void;
  onClose: () => void;
  onSettingsChanged: () => void;
}

export function Sidebar({
  boards,
  activeId,
  open,
  onSelect,
  onCreate,
  onClose,
  onSettingsChanged,
}: Props) {
  const [url, setUrl] = useState(getApiUrl());

  function saveUrl() {
    setApiUrl(url.trim());
    onSettingsChanged();
  }

  return (
    <aside className={"sidebar" + (open ? " open" : "")}>
      <div className="brand">
        <span className="logo">🧾</span>
        <span>TaskBoard</span>
        <button className="nav-close" onClick={onClose} aria-label="Close boards">
          ✕
        </button>
      </div>

      <div className="section-label">Subjects</div>
      <nav className="board-list">
        {boards.map((b) => (
          <button
            key={b.id}
            className={"board-item" + (b.id === activeId ? " active" : "")}
            onClick={() => onSelect(b.id)}
          >
            {b.name}
          </button>
        ))}
      </nav>
      <button className="new-board" onClick={onCreate}>
        + New board
      </button>

      <div className="settings">
        <div className="section-label">API URL</div>
        <input value={url} onChange={(e) => setUrl(e.target.value)} onBlur={saveUrl} spellCheck={false} />
      </div>
    </aside>
  );
}
