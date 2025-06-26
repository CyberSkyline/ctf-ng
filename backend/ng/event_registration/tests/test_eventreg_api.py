"""
/backend/ng/event_registration/tests/test_eventreg_api.py
Event Registration API endpoint tests package.
"""

import pytest
from ng.user.models.User import User
from flask import g
from datetime import datetime
from ..models.Demographic import Demographic
from datetime import timedelta

pytestmark = pytest.mark.db

def test_get_demographic_authenticated(logged_in_client,event):
    """Check that user demographic endpoint works for authenticated users."""
    g.user = User(id=1)
    Demographic.create_demographic(
        user_id=g.user.id,
        event_id=event.id,
        reg_timestamp=datetime.utcnow()
    )
    response = logged_in_client.get("/ng/event_registration", query_string={"event_id": event.id})
    print(response.get_json())
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "demographic" in data
    assert len(data["demographic"]) > 0

def test_get_demographic_unauthenticated(client, event):
    """Check that user demographic endpoint requires authentication."""
    response = client.get("/ng/event_registration", query_string={"event_id": event.id})
    assert response.status_code == 302  # Redirect to login
    assert response.location is not None

def test_join_event_new_team(logged_in_client, event_registration):
    """Check that joining an event with a new team works."""
    data = {
        "event_id": event_registration.event_id,
        "team_name": "New Team"
    }
    response = logged_in_client.post("/ng/event_registration/join_event", json=data)
    assert response.status_code == 200

def test_join_event_existing_team(logged_in_client, event_registration, team_with_members):
    """Check that joining an event with an existing team works."""
    data = {
        "event_id": event_registration.event_id,
        "invite_code": team_with_members["team"].invite_code
    }
    response = logged_in_client.post("/ng/event_registration/join_event", json=data)
    assert response.status_code == 200
    assert response.get_json()["success"] is True

def test_join_closed_event_fails(logged_in_client, closed_event_registration):
    """Check that joining a closed event fails."""
    data = {
        "event_id": closed_event_registration.event_id,
        "team_name": "New Team"
    }
    response = logged_in_client.post("/ng/event_registration/join_event", json=data)
    assert response.status_code == 403
    assert "Event Registration is not open" in response.get_json()["errors"]["event_registration_closed"]
    

def test_join_event_past_registration_period_fails(logged_in_client, past_event_registration):
    """Check that joining an event after the registration period fails."""
    data = {
        "event_id": past_event_registration.event_id,
        "team_name": "New Team"
    }
    response = logged_in_client.post("/ng/event_registration/join_event", json=data)
    assert response.status_code == 403
    assert "Event Registration has ended" in response.get_json()["errors"]["event_registration_ended"]

def test_join_event_before_registration_starts_fails(logged_in_client, future_event_registration):
    """Check that joining an event before the registration starts fails."""
    data = {
        "event_id": future_event_registration.event_id,
        "team_name": "New Team"
    }
    response = logged_in_client.post("/ng/event_registration/join_event", json=data)
    assert response.status_code == 403
    assert "Event Registration has not started yet" in response.get_json()["errors"]["event_registration_not_started"]

def test_can_only_register_once(logged_in_client, event_registration, team_with_members):
    """Check that a user can only register once for an event."""
    data = {
        "event_id": event_registration.event_id,
        "invite_code": team_with_members["team"].invite_code
    }
    response = logged_in_client.post("/ng/event_registration/join_event", json=data)
    assert response.status_code == 200
    response = logged_in_client.post("/ng/event_registration/join_event", json=data)
    print(response.get_json())
    assert response.status_code == 400
    assert "User is already in team" in response.get_json()["error"]

def test_create_registration_period(admin_client, event):
    """Check that creating a registration period works."""
    data = {
        "event_id": event.id,
        "reg_open": True,
        "reg_start_date": datetime.utcnow().isoformat(),
        "reg_end_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    response = admin_client.post("/ng/event_registration/create_registration_period", json=data)
    print(response.get_json())
    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_create_registration_period_invalid_dates(admin_client, event):
    """Check that creating a registration period with invalid dates fails."""
    data = {
        "event_id": event.id,
        "reg_open": True,
        "reg_start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "reg_end_date": datetime.utcnow().isoformat()  # End date before start date
    }
    response = admin_client.post("/ng/event_registration/create_registration_period", json=data)
    assert response.status_code == 400
    assert "Start time must be before end time" in response.get_json()["error"]["reg_end_date"]

def test_create_registration_only_admin(logged_in_client, event):
    """Check that only admins can create a registration period."""
    data = {
        "event_id": event.id,
        "reg_open": True,
        "reg_start_date": datetime.utcnow().isoformat(),
        "reg_end_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    response = logged_in_client.post("/ng/event_registration/create_registration_period", json=data)
    assert response.status_code == 403  # Forbidden
    assert "You don't have the permission" in response.get_json()["message"]
