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
import type { Board, Task, TaskBoardClient } from "@taskboard/shared";
import { theme } from "../theme";

interface Props {
  client: TaskBoardClient;
  boardId: number;
  taskId: number;
  onBack: () => void;
}

export function TaskScreen({ client, boardId, taskId, onBack }: Props) {
  const [board, setBoard] = useState<Board | null>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const b = await client.getBoard(boardId);
    setBoard(b);
    setTask(b.tasks.find((t) => t.id === taskId) ?? null);
  }, [client, boardId, taskId]);

  useEffect(() => {
    load();
  }, [load]);

  async function move(statusId: number) {
    if (!task || statusId === task.status_id) return;
    setBusy(true);
    try {
      await client.moveTask(task.id, { status_id: statusId });
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function addComment() {
    if (!comment.trim() || !task) return;
    await client.addComment(task.id, comment.trim());
    setComment("");
    load();
  }

  if (!board || !task) {
    return (
      <View style={styles.container}>
        <Pressable onPress={onBack}>
          <Text style={styles.link}>‹ Back</Text>
        </Pressable>
        <ActivityIndicator color={theme.accent} style={{ marginTop: 24 }} />
      </View>
    );
  }

  const statuses = [...board.statuses].sort((a, b) => a.position - b.position);
  const lane = board.swimlanes.find((l) => l.id === task.swimlane_id);

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      <Pressable onPress={onBack}>
        <Text style={styles.link}>‹ {board.name}</Text>
      </Pressable>

      <Text style={styles.chip}>{lane?.name}</Text>
      <Text style={styles.h1}>{task.title}</Text>

      <View style={styles.bar}>
        <View style={[styles.barFill, { width: `${task.progress}%` }]} />
      </View>
      <Text style={styles.progressLabel}>{task.progress}% complete</Text>

      <Text style={styles.label}>Move to (prints a receipt)</Text>
      <View style={styles.statusRow}>
        {statuses.map((s) => {
          const active = s.id === task.status_id;
          return (
            <Pressable
              key={s.id}
              disabled={busy}
              style={[styles.statusBtn, active && styles.statusBtnActive]}
              onPress={() => move(s.id)}
            >
              <Text style={[styles.statusBtnText, active && styles.statusBtnTextActive]}>
                {s.name}
              </Text>
            </Pressable>
          );
        })}
      </View>

      <Text style={styles.label}>Comments ({task.comments.length})</Text>
      {task.comments.map((c) => (
        <View key={c.id} style={styles.comment}>
          <Text style={styles.commentAuthor}>{c.author}</Text>
          <Text style={styles.commentBody}>{c.body}</Text>
        </View>
      ))}
      {task.comments.length === 0 && <Text style={styles.muted}>No comments yet.</Text>}

      <View style={styles.addRow}>
        <TextInput
          style={styles.input}
          value={comment}
          onChangeText={setComment}
          placeholder="Write a comment…"
          placeholderTextColor={theme.muted}
          onSubmitEditing={addComment}
        />
        <Pressable style={styles.smallBtn} onPress={addComment}>
          <Text style={styles.smallBtnText}>Add</Text>
        </Pressable>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  link: { color: theme.accent, fontSize: 14, marginBottom: 10 },
  chip: { color: theme.muted, fontSize: 12 },
  h1: { color: theme.text, fontSize: 22, fontWeight: "700", marginBottom: 14 },
  bar: { height: 8, backgroundColor: "#0d1117", borderRadius: 999, overflow: "hidden" },
  barFill: { height: "100%", backgroundColor: theme.green },
  progressLabel: { color: theme.muted, fontSize: 12, marginTop: 6 },
  label: {
    color: theme.muted,
    fontSize: 11,
    textTransform: "uppercase",
    letterSpacing: 1,
    marginTop: 20,
    marginBottom: 8,
  },
  statusRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  statusBtn: {
    backgroundColor: theme.panel,
    borderColor: theme.border,
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  statusBtnActive: { backgroundColor: theme.accent, borderColor: theme.accent },
  statusBtnText: { color: theme.text, fontSize: 13 },
  statusBtnTextActive: { color: "#fff", fontWeight: "600" },
  comment: {
    backgroundColor: theme.panel,
    borderColor: theme.border,
    borderWidth: 1,
    borderRadius: 10,
    padding: 10,
    marginBottom: 8,
  },
  commentAuthor: { color: theme.accent2, fontSize: 11, marginBottom: 2 },
  commentBody: { color: theme.text, fontSize: 14 },
  muted: { color: theme.muted, fontSize: 13 },
  addRow: { flexDirection: "row", gap: 8, marginTop: 10 },
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
});
