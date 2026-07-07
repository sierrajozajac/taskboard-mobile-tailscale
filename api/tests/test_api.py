"""End-to-end API tests. Printing runs in console mode, so create/move exercise
the real print code path (formatting a receipt) without any hardware."""

from __future__ import annotations


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_board_seeds_swimlanes(board):
    names = [s["name"] for s in board["swimlanes"]]
    assert names == ["Pending", "In Progress", "Complete"]
    assert board["tasks"] == []


def test_create_task_defaults_to_first_swimlane(client, board):
    r = client.post("/tasks", json={"board_id": board["id"], "title": "Ship it"})
    assert r.status_code == 201, r.text
    task = r.json()
    first_lane = board["swimlanes"][0]["id"]
    assert task["swimlane_id"] == first_lane
    assert task["title"] == "Ship it"
    assert task["progress"] == 0


def test_move_task_changes_swimlane_and_complete_finishes(client, board):
    task = client.post("/tasks", json={"board_id": board["id"], "title": "Do the thing"}).json()

    complete = next(s for s in board["swimlanes"] if s["name"] == "Complete")["id"]
    r = client.post(f"/tasks/{task['id']}/move", json={"swimlane_id": complete})
    assert r.status_code == 200, r.text
    moved = r.json()
    assert moved["swimlane_id"] == complete
    assert moved["progress"] == 100  # auto-completed in a done-style swimlane


def test_move_rejects_swimlane_from_another_board(client, board):
    other = client.post("/boards", json={"name": "Other"}).json()
    task = client.post("/tasks", json={"board_id": board["id"], "title": "t"}).json()
    foreign_lane = other["swimlanes"][0]["id"]
    r = client.post(f"/tasks/{task['id']}/move", json={"swimlane_id": foreign_lane})
    assert r.status_code == 400


def test_create_swimlane_and_place_task(client, board):
    lane = client.post(f"/boards/{board['id']}/swimlanes", json={"name": "Blocked"}).json()
    task = client.post(
        "/tasks", json={"board_id": board["id"], "swimlane_id": lane["id"], "title": "stuck"}
    ).json()
    assert task["swimlane_id"] == lane["id"]


def test_comments_roundtrip(client, board):
    task = client.post("/tasks", json={"board_id": board["id"], "title": "t"}).json()
    c = client.post(f"/tasks/{task['id']}/comments", json={"body": "first note"})
    assert c.status_code == 201, c.text
    listing = client.get(f"/tasks/{task['id']}/comments").json()
    assert [x["body"] for x in listing] == ["first note"]


def test_get_board_nests_tasks_and_comments(client, board):
    task = client.post("/tasks", json={"board_id": board["id"], "title": "nested"}).json()
    client.post(f"/tasks/{task['id']}/comments", json={"body": "hi"})

    full = client.get(f"/boards/{board['id']}").json()
    assert len(full["tasks"]) == 1
    assert full["tasks"][0]["comments"][0]["body"] == "hi"


def test_delete_board_cascades(client, board):
    client.post("/tasks", json={"board_id": board["id"], "title": "t"})
    assert client.delete(f"/boards/{board['id']}").status_code == 204
    assert client.get(f"/boards/{board['id']}").status_code == 404
