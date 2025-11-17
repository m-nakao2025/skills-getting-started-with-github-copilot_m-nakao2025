from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset module-level activities state before/after each test so tests are idempotent."""
    original = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    # Basic checks for expected keys
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister(client):
    email = "testuser@mergington.edu"
    # Sign up succeeds
    res = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert res.status_code == 200
    assert "Signed up" in res.json()["message"]

    # Now unregister
    res2 = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
    assert res2.status_code == 200
    assert "Unregistered" in res2.json()["message"]


def test_duplicate_signup_fails(client):
    # michael is already in Chess Club in initial data
    email = "michael@mergington.edu"
    res = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert res.status_code == 400


def test_unregister_nonexistent_returns_404(client):
    email = "noone@mergington.edu"
    res = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
    assert res.status_code == 404
