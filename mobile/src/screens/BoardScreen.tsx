import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import type { Board, Swimlane, TaskBoardClient } from "@taskboard/shared";
import { theme } from "../theme";

interface Props {
  client: TaskBoardClient;
  boardId: number;
  onBack: () => void;
  onOpenTask: (taskId: number) => void;
}

export function BoardScreen({ client, boardId, onBack, onOpenTask }: Props) {
  const [board, setBoard] = useState<Board | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [laneId, setLaneId] = useState<number | null>(null); // swimlane to add into

  const load = useCallback(async () => {
    try {
      setBoard(await client.getBoard(boardId));
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [client, boardId]);

  useEffect(() => {
    load();
  }, [load]);

  // Default the "add to" swimlane to the first column once the board loads.
  useEffect(() => {
    if (!board) return;
    const lanes = [...board.swimlanes].sort((a, b) => a.position - b.position);
    if (lanes.length && (laneId == null || !lanes.some((l) => l.id === laneId))) {
      setLaneId(lanes[0].id);
    }
  }, [board, laneId]);

  async function addTask() {
    if (!newTitle.trim() || !board || laneId == null) return;
    await client.createTask({
      board_id: boardId,
      swimlane_id: laneId,
      title: newTitle.trim(),
    });
    setNewTitle("");
    load();
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Header title="Board" onBack={onBack} />
        <Text style={styles.error}>{error}</Text>
      </View>
    );
  }
  if (!board) {
    return (
      <View style={styles.container}>
        <Header title="Board" onBack={onBack} />
        <ActivityIndicator color={theme.accent} style={{ marginTop: 24 }} />
      </View>
    );
  }

  const swimlanes = [...board.swimlanes].sort((a, b) => a.position - b.position);

  return (
    <View style={styles.container}>
      <Header title={board.name} onBack={onBack} />

      <View style={styles.addRow}>
        <TextInput
          style={styles.input}
          value={newTitle}
          onChangeText={setNewTitle}
          placeholder="New task…"
          placeholderTextColor={theme.muted}
          onSubmitEditing={addTask}
        />
        <Pressable style={styles.smallBtn} onPress={addTask}>
          <Text style={styles.smallBtnText}>Add</Text>
        </Pressable>
      </View>

      {swimlanes.length > 1 && (
        <View style={styles.laneChips}>
          <Text style={styles.addToLabel}>Add to:</Text>
          {swimlanes.map((lane) => {
            const active = lane.id === laneId;
            return (
              <Pressable
                key={lane.id}
                style={[styles.laneChip, active && styles.laneChipActive]}
                onPress={() => setLaneId(lane.id)}
              >
                <Text style={[styles.laneChipText, active && styles.laneChipTextActive]}>
                  {lane.name}
                </Text>
              </Pressable>
            );
          })}
        </View>
      )}

      <ScrollView>
        {swimlanes.map((lane: Swimlane) => {
          const tasks = board.tasks
            .filter((t) => t.swimlane_id === lane.id)
            .sort((a, b) => a.position - b.position);
          return (
            <View key={lane.id} style={styles.column}>
              <Text style={styles.colHead}>
                {lane.name} · {tasks.length}
              </Text>
              {tasks.map((t) => (
                <Pressable key={t.id} style={styles.task} onPress={() => onOpenTask(t.id)}>
                  <Text style={styles.taskTitle}>{t.title}</Text>
                  <View style={styles.taskMeta}>
                    <Text style={styles.taskProgress}>{t.progress}%</Text>
                  </View>
                  <View style={styles.bar}>
                    <View style={[styles.barFill, { width: `${t.progress}%` }]} />
                  </View>
                </Pressable>
              ))}
              {tasks.length === 0 && <Text style={styles.muted}>—</Text>}
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

function Header({ title, onBack }: { title: string; onBack: () => void }) {
  return (
    <View style={styles.header}>
      <Pressable onPress={onBack}>
        <Text style={styles.link}>‹ Boards</Text>
      </Pressable>
      <Text style={styles.h1}>{title}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  header: { marginBottom: 8 },
  link: { color: theme.accent, fontSize: 14, marginBottom: 4 },
  h1: { color: theme.text, fontSize: 22, fontWeight: "700" },
  error: { color: "#f3b1b1", marginTop: 16 },
  addRow: { flexDirection: "row", gap: 8, marginBottom: 12 },
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
  smallBtn: { backgroundColor: theme.accent, borderRadius: 8, paddingHorizontal: 14, justifyContent: "center" },
  smallBtnText: { color: "#fff", fontWeight: "600" },
  laneChips: {
    flexDirection: "row",
    flexWrap: "wrap",
    alignItems: "center",
    gap: 6,
    marginBottom: 14,
  },
  addToLabel: { color: theme.muted, fontSize: 12, marginRight: 2 },
  laneChip: {
    backgroundColor: theme.panel,
    borderColor: theme.border,
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  laneChipActive: { backgroundColor: theme.accent, borderColor: theme.accent },
  laneChipText: { color: theme.text, fontSize: 12 },
  laneChipTextActive: { color: "#fff", fontWeight: "600" },
  column: { marginBottom: 18 },
  colHead: {
    color: theme.muted,
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 8,
    borderBottomColor: theme.border,
    borderBottomWidth: 2,
    paddingBottom: 4,
  },
  task: {
    backgroundColor: theme.panel,
    borderColor: theme.border,
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
  },
  taskTitle: { color: theme.text, fontSize: 15 },
  taskMeta: { flexDirection: "row", justifyContent: "space-between", marginTop: 6, marginBottom: 6 },
  taskLane: { color: theme.accent2, fontSize: 12 },
  taskProgress: { color: theme.muted, fontSize: 12 },
  bar: { height: 5, backgroundColor: "#0d1117", borderRadius: 999, overflow: "hidden" },
  barFill: { height: "100%", backgroundColor: theme.green },
  muted: { color: theme.muted, fontSize: 13 },
});
