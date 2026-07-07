import { TaskBoardClient } from "@taskboard/shared";

const STORAGE_KEY = "taskboard.apiUrl";
export const DEFAULT_API_URL = "http://127.0.0.1:8000";

export function getApiUrl(): string {
  return localStorage.getItem(STORAGE_KEY) ?? DEFAULT_API_URL;
}

export function setApiUrl(url: string): void {
  localStorage.setItem(STORAGE_KEY, url);
}

export function makeClient(): TaskBoardClient {
  return new TaskBoardClient(getApiUrl());
}
