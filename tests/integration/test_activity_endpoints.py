from fastapi.testclient import TestClient


def test_activities_can_be_listed_filtered_and_read(
    client: TestClient,
    register_user,
    create_todo,
    create_comment,
) -> None:
    account = register_user("activities@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}
    todo = create_todo(account["access_token"])
    create_comment(account["access_token"], todo["id"])

    listed = client.get("/api/activities", headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] == 2
    assert {item["action"] for item in listed.json()["items"]} == {"created"}

    filtered = client.get(
        "/api/activities",
        headers=headers,
        params={"todo_id": todo["id"]},
    )
    assert filtered.status_code == 200, filtered.text
    assert filtered.json()["total"] == 2
    activity = filtered.json()["items"][0]

    read = client.get(f"/api/activities/{activity['id']}", headers=headers)
    assert read.status_code == 200, read.text
    assert read.json()["id"] == activity["id"]
    assert read.json()["todo_id"] == todo["id"]
