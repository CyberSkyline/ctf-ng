"""
/backend/ctfd/plugin/tests/api/test_event_api.py
API Tests for event endpoints
"""

import pytest

pytestmark = pytest.mark.db


def test_events_endpoint_with_authentication(logged_in_client):
    """Check that events endpoint works for an authenticated user."""
    response = logged_in_client.get("/plugin/api/events")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "events" in data["data"]


def test_create_event_is_forbidden_for_normal_user(logged_in_client):
    """Check that normal users cannot create events."""
    data = {"name": "Test Event", "description": "Test event description"}
    response = logged_in_client.post("/plugin/api/events", json=data)
    assert response.status_code in [302, 403]
    if response.status_code == 302:
        assert response.location is not None
    else:
        data = response.get_json()
        assert data is not None


def test_create_event_succeeds_for_admin_user(admin_client):
    """Check that admin users can create events."""
    data = {
        "name": "Admin Event",
        "description": "Event created by admin",
        "max_team_size": 4,
    }
    response = admin_client.post("/plugin/api/events", json=data)
    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["success"]
    assert response_data["data"]["event"]["name"] == "Admin Event"
    assert response_data["data"]["event"]["max_team_size"] == 4
