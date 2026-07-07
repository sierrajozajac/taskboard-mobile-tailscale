import { TaskBoardClient } from "@taskboard/shared";

const STORAGE_KEY = "taskboard.apiUrl";

// When the board is served by the API itself (browser over Tailscale/LAN), default
// to that same origin. In the Tauri desktop shell (tauri://… origin) fall back to
// the local API. Either way, the sidebar field can override it.
function defaultApiUrl(): string {
  if (typeof window !== "undefined" && window.location.protocol.startsWith("http")) {
    return window.location.origin;
  }
  return "http://127.0.0.1:8000";
}

export const DEFAULT_API_URL = defaultApiUrl();

export function getApiUrl(): string {
  return localStorage.getItem(STORAGE_KEY) ?? DEFAULT_API_URL;
}

export function setApiUrl(url: string): void {
  localStorage.setItem(STORAGE_KEY, url);
}

export function makeClient(): TaskBoardClient {
  return new TaskBoardClient(getApiUrl());
}
