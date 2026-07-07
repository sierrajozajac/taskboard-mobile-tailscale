import AsyncStorage from "@react-native-async-storage/async-storage";
import { TaskBoardClient } from "@taskboard/shared";

// Phones can't reach the PC via localhost — set this to the PC's LAN or Tailscale
// address (e.g. http://100.x.y.z:8000). Editable on the Boards screen and
// persisted across launches with AsyncStorage.
export const DEFAULT_API_URL = "http://192.168.1.20:8000";

const STORAGE_KEY = "taskboard.apiUrl";

export function makeClient(url: string): TaskBoardClient {
  return new TaskBoardClient(url);
}

export async function loadApiUrl(): Promise<string> {
  try {
    return (await AsyncStorage.getItem(STORAGE_KEY)) ?? DEFAULT_API_URL;
  } catch {
    return DEFAULT_API_URL;
  }
}

export async function saveApiUrl(url: string): Promise<void> {
  try {
    await AsyncStorage.setItem(STORAGE_KEY, url);
  } catch {
    /* ignore persistence failures */
  }
}
