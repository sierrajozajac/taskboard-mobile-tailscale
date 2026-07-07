import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import type { BoardSummary, TaskBoardClient } from "@taskboard/shared";
import { theme } from "../theme";

interface Props {
  client: TaskBoardClient;
  apiUrl: string;
  onApiUrlChange: (url: string) => void;
  onOpenBoard: (boardId: number) => void;
}

export function BoardsScreen({ client, apiUrl, onApiUrlChange, onOpenBoard }: Props) {
  const [boards, setBoards] = useState<BoardSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [draftUrl, setDraftUrl] = useState(apiUrl);
  const [newBoard, setNewBoard] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setBoards(await client.listBoards());
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [client]);

  useEffect(() => {
    load();
  }, [load]);

  // Reflect the persisted URL once it loads asynchronously at startup.
  useEffect(() => {
    setDraftUrl(apiUrl);
  }, [apiUrl]);

  async function createBoard() {
    const name = newBoard.trim();
    if (!name) return;
    try {
      const created = await client.createBoard(name);
      setNewBoard("");
      onOpenBoard(created.id); // open it, like the desktop does
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.h1}>🧾 TaskBoard</Text>

      <Text style={styles.label}>API URL</Text>
      <View style={styles.row}>
        <TextInput
          style={styles.input}
          value={draftUrl}
          onChangeText={setDraftUrl}
          autoCapitalize="none"
          autoCorrect={false}
          placeholder="http://192.168.x.x:8000"
          placeholderTextColor={theme.muted}
        />
        <Pressable style={styles.smallBtn} onPress={() => onApiUrlChange(draftUrl.trim())}>
          <Text style={styles.smallBtnText}>Set</Text>
        </Pressable>
      </View>

      <View style={styles.rowBetween}>
        <Text style={styles.label}>Subjects</Text>
        <Pressable onPress={load}>
          <Text style={styles.link}>Refresh</Text>
        </Pressable>
      </View>

      <View style={styles.row}>
        <TextInput
          style={styles.input}
          value={newBoard}
          onChangeText={setNewBoard}
          placeholder="New board…"
          placeholderTextColor={theme.muted}
          onSubmitEditing={createBoard}
        />
        <Pressable style={styles.smallBtn} onPress={createBoard}>
          <Text style={styles.smallBtnText}>Create</Text>
        </Pressable>
      </View>

      {loading && <ActivityIndicator color={theme.accent} style={{ marginTop: 20 }} />}
      {error && <Text style={styles.error}>Can't reach the API: {error}</Text>}

      <FlatList
        data={boards}
        keyExtractor={(b) => String(b.id)}
        renderItem={({ item }) => (
          <Pressable style={styles.card} onPress={() => onOpenBoard(item.id)}>
            <Text style={styles.cardTitle}>{item.name}</Text>
            {!!item.description && <Text style={styles.cardSub}>{item.description}</Text>}
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  h1: { color: theme.text, fontSize: 24, fontWeight: "700", marginBottom: 12 },
  label: {
    color: theme.muted,
    fontSize: 11,
    textTransform: "uppercase",
    letterSpacing: 1,
    marginTop: 12,
    marginBottom: 6,
  },
  row: { flexDirection: "row", gap: 8 },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  input: {
    flex: 1,
    backgroundColor: theme.panel,
    color: theme.text,
    borderColor: theme.border,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  smallBtn: {
    backgroundColor: theme.accent,
    borderRadius: 8,
    paddingHorizontal: 14,
    justifyContent: "center",
  },
  smallBtnText: { color: "#fff", fontWeight: "600" },
  link: { color: theme.accent, fontSize: 13 },
  error: { color: "#f3b1b1", marginTop: 10 },
  card: {
    backgroundColor: theme.panel,
    borderColor: theme.border,
    borderWidth: 1,
    borderRadius: 10,
    padding: 14,
    marginTop: 10,
  },
  cardTitle: { color: theme.text, fontSize: 16, fontWeight: "600" },
  cardSub: { color: theme.muted, fontSize: 13, marginTop: 4 },
});
