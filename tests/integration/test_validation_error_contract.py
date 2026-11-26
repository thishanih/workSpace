from fastapi.testclient import TestClient


def test_validation_response_omits_submitted_fields_and_values(
    client: TestClient,
) -> None:
    submitted_values = [
        "invalid-email-secret",
        "name-secret" * 11,
        "pw-secr",
    ]

    response = client.post(
        "/api/auth/register",
        json={
            "email": submitted_values[0],
            "name": submitted_values[1],
            "password": submitted_values[2],
        },
    )

    assert response.status_code == 422, response.text
    body = response.json()
    assert set(body) == {"detail"}
    assert len(body["detail"]) == 3
    assert all(set(issue) == {"loc", "msg", "type"} for issue in body["detail"])
    assert all(issue["loc"][0] == "body" for issue in body["detail"])
    for submitted_value in submitted_values:
        assert submitted_value not in response.text
    for private_key in ('"input"', '"ctx"', '"url"', "Traceback"):
        assert private_key not in response.text


def test_malformed_json_validation_response_omits_raw_body(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("malformed-error@example.com")
    raw_body = '{"title":"raw-body-secret'

    response = client.post(
        "/api/todos",
        headers={"Authorization": f"Bearer {account['access_token']}"},
        content=raw_body,
    )

    assert response.status_code == 422, response.text
    body = response.json()
    assert set(body) == {"detail"}
    assert all(set(issue) == {"loc", "msg", "type"} for issue in body["detail"])
    assert raw_body not in response.text
    assert "raw-body-secret" not in response.text
