import { TaskBoardClient } from "@taskboard/shared";

// Phones can't reach the PC via localhost — set this to the PC's LAN IP, e.g.
// http://192.168.1.20:8000 . Editable at runtime on the Boards screen.
export const DEFAULT_API_URL = "http://192.168.1.20:8000";

export function makeClient(url: string): TaskBoardClient {
  return new TaskBoardClient(url);
}
