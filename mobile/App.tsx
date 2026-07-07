import { useCallback, useEffect, useMemo, useState } from "react";
import { SafeAreaView, StyleSheet } from "react-native";
import { StatusBar } from "expo-status-bar";
import { DEFAULT_API_URL, loadApiUrl, makeClient, saveApiUrl } from "./src/api";
import { theme } from "./src/theme";
import { BoardsScreen } from "./src/screens/BoardsScreen";
import { BoardScreen } from "./src/screens/BoardScreen";
import { TaskScreen } from "./src/screens/TaskScreen";

type Screen =
  | { name: "boards" }
  | { name: "board"; boardId: number }
  | { name: "task"; boardId: number; taskId: number };

export default function App() {
  const [apiUrl, setApiUrl] = useState(DEFAULT_API_URL);
  const [screen, setScreen] = useState<Screen>({ name: "boards" });
  const client = useMemo(() => makeClient(apiUrl), [apiUrl]);

  // Load the saved API URL once on launch.
  useEffect(() => {
    loadApiUrl().then(setApiUrl);
  }, []);

  const changeApiUrl = useCallback((url: string) => {
    setApiUrl(url);
    saveApiUrl(url);
  }, []);

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar style="light" />
      {screen.name === "boards" && (
        <BoardsScreen
          client={client}
          apiUrl={apiUrl}
          onApiUrlChange={changeApiUrl}
          onOpenBoard={(boardId) => setScreen({ name: "board", boardId })}
        />
      )}
      {screen.name === "board" && (
        <BoardScreen
          client={client}
          boardId={screen.boardId}
          onBack={() => setScreen({ name: "boards" })}
          onOpenTask={(taskId) => setScreen({ name: "task", boardId: screen.boardId, taskId })}
        />
      )}
      {screen.name === "task" && (
        <TaskScreen
          client={client}
          boardId={screen.boardId}
          taskId={screen.taskId}
          onBack={() => setScreen({ name: "board", boardId: screen.boardId })}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: theme.bg,
  },
});
