import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["existing@example.test"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == app_module.activities


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@example.test"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@example.test for Chess Club"
    }
    assert "new@example.test" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@example.test"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new@example.test"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "existing@example.test"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@example.test from Chess Club"
    }
    assert "existing@example.test" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_missing_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "missing@example.test"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "existing@example.test"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}