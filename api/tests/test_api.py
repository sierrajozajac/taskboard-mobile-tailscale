"""End-to-end API tests. Printing runs in console mode, so create/move exercise
the real print code path (formatting a receipt) without any hardware."""

from __future__ import annotations


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_board_seeds_columns_and_lane(board):
    names = [s["name"] for s in board["statuses"]]
    assert names == ["Backlog", "To Do", "In Progress", "Done"]
    assert [l["name"] for l in board["swimlanes"]] == ["General"]
    assert board["tasks"] == []


def test_create_task_defaults_to_first_column(client, board):
    lane = board["swimlanes"][0]["id"]
    r = client.post("/tasks", json={"board_id": board["id"], "swimlane_id": lane, "title": "Ship it"})
    assert r.status_code == 201, r.text
    task = r.json()
    first_col = board["statuses"][0]["id"]
    assert task["status_id"] == first_col
    assert task["title"] == "Ship it"
    assert task["progress"] == 0


def test_move_task_changes_status_and_done_completes(client, board):
    lane = board["swimlanes"][0]["id"]
    task = client.post(
        "/tasks", json={"board_id": board["id"], "swimlane_id": lane, "title": "Do the thing"}
    ).json()

    done_col = next(s for s in board["statuses"] if s["name"] == "Done")["id"]
    r = client.post(f"/tasks/{task['id']}/move", json={"status_id": done_col})
    assert r.status_code == 200, r.text
    moved = r.json()
    assert moved["status_id"] == done_col
    assert moved["progress"] == 100  # auto-completed in the Done column


def test_move_rejects_status_from_another_board(client, board):
    other = client.post("/boards", json={"name": "Other"}).json()
    lane = board["swimlanes"][0]["id"]
    task = client.post(
        "/tasks", json={"board_id": board["id"], "swimlane_id": lane, "title": "t"}
    ).json()
    foreign_col = other["statuses"][0]["id"]
    r = client.post(f"/tasks/{task['id']}/move", json={"status_id": foreign_col})
    assert r.status_code == 400


def test_comments_roundtrip(client, board):
    lane = board["swimlanes"][0]["id"]
    task = client.post(
        "/tasks", json={"board_id": board["id"], "swimlane_id": lane, "title": "t"}
    ).json()
    c = client.post(f"/tasks/{task['id']}/comments", json={"body": "first note"})
    assert c.status_code == 201, c.text
    listing = client.get(f"/tasks/{task['id']}/comments").json()
    assert [x["body"] for x in listing] == ["first note"]


def test_get_board_nests_tasks_and_comments(client, board):
    lane = board["swimlanes"][0]["id"]
    task = client.post(
        "/tasks", json={"board_id": board["id"], "swimlane_id": lane, "title": "nested"}
    ).json()
    client.post(f"/tasks/{task['id']}/comments", json={"body": "hi"})

    full = client.get(f"/boards/{board['id']}").json()
    assert len(full["tasks"]) == 1
    assert full["tasks"][0]["comments"][0]["body"] == "hi"


def test_delete_board_cascades(client, board):
    lane = board["swimlanes"][0]["id"]
    client.post("/tasks", json={"board_id": board["id"], "swimlane_id": lane, "title": "t"})
    assert client.delete(f"/boards/{board['id']}").status_code == 204
    assert client.get(f"/boards/{board['id']}").status_code == 404
