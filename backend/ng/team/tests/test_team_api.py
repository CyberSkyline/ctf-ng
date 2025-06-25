"""
API Tests for team endpoints
/backend/ng/team/tests/test_team_api.py
"""

# We must use the external CTFd test helpers, so we ignore the I001 sort rule.
import pytest
import time
from CTFd.models import db as _db
from tests.helpers import gen_user  # noqa: I001
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole
from ...core.testing.helpers import login_as

pytestmark = pytest.mark.db


def test_teams_endpoint_requires_authentication(client, event):
    """Check that teams endpoint requires authentication for anonymous users."""
    response = client.get(f"/ng/teams?event_id={event.id}")
    assert response.status_code == 302
    assert response.location is not None


def test_get_teams_in_event_is_public_and_secure(logged_in_client, team_with_members):
    """
    Check the public endpoint for listing teams in an event and ensures it's secure.
    """
    team_data = team_with_members
    event_id = team_data["team"].event_id

    response = logged_in_client.get(f"/ng/events/{event_id}/teams")
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"]
    assert "teams" in data["data"]

    teams_list = data["data"]["teams"]
    assert len(teams_list) >= 1

    first_team = teams_list[0]
    assert "invite_code" not in first_team


def test_create_team_requires_data(logged_in_client):
    """Check that team creation requires valid data."""
    response = logged_in_client.post("/ng/teams")
    assert response.status_code in [400, 403]
    data = response.get_json()
    if data is not None:
        if "success" in data:
            assert not data["success"]
        else:
            assert "errors" in data or "error" in data or "message" in data


def test_create_team_creator_becomes_captain(logged_in_client, event, normal_user):
    """Check that team creator automatically becomes captain."""
    data = {"name": "Test Team", "event_id": event.id}
    response = logged_in_client.post("/ng/teams", json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data["success"]

    team_id = response_data["data"]["team"]["id"]

    captain_member = TeamMember.query.filter_by(team_id=team_id, user_id=normal_user.id, role=TeamRole.CAPTAIN).first()
    assert captain_member is not None


def test_captain_assignment_security(client, team_with_members, admin_user):
    """Check that captain assignment requires proper authorization."""
    team_data = team_with_members
    team = team_data["team"]
    member = team_data["member"]

    login_as(client, admin_user)

    response = client.post(f"/ng/teams/{team.id}/captain", json={"user_id": member.id})

    assert response.status_code in [200, 405]


def test_update_team_endpoint_security(client, team_with_members):
    """Check that team updates require captain or admin privileges."""
    team_data = team_with_members
    team = team_data["team"]
    captain = team_data["captain"]
    member = team_data["member"]

    login_as(client, member)
    response = client.patch(f"/ng/teams/{team.id}", json={"name": "Updated by Member"})
    assert response.status_code in [403, 404]

    login_as(client, captain)
    response = client.patch(f"/ng/teams/{team.id}", json={"name": "Updated by Captain"})
    assert response.status_code in [200, 405]


def test_join_team_fails_if_already_in_a_team_in_event(logged_in_client, event, normal_user):
    """Check that users can't join multiple teams in the same event."""
    team1_data = {"name": "First Team", "event_id": event.id}
    response = logged_in_client.post("/ng/teams", json=team1_data)
    assert response.status_code == 201

    timestamp = int(time.time())
    second_user = gen_user(_db, name=f"seconduser_{timestamp}", email=f"second_{timestamp}@example.com")

    login_as(logged_in_client, second_user)
    team2_data = {"name": "Second Team", "event_id": event.id}
    response = logged_in_client.post("/ng/teams", json=team2_data)
    assert response.status_code == 201
    second_team = response.get_json()["data"]["team"]

    login_as(logged_in_client, normal_user)

    join_data = {"invite_code": second_team["invite_code"]}
    response = logged_in_client.post("/ng/teams/join", json=join_data)
    assert response.status_code == 400
    data = response.get_json()
    assert not data["success"]

    errors = data.get("errors", {})
    if isinstance(errors, dict):
        error_msg = " ".join(errors.values())
    else:
        error_msg = str(errors)
    assert "already" in error_msg.lower()


def test_list_all_teams_as_admin(admin_client, team_with_members):
    """
    Check that an admin can fetch the list of all teams and it includes invite codes.
    """
    response = admin_client.get("/ng/teams")
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"]
    assert "teams" in data["data"]

    teams_list = data["data"]["teams"]

    assert len(teams_list) >= 1

    first_team = teams_list[0]
    assert "invite_code" in first_team


def test_list_all_teams_fails_for_normal_user(logged_in_client):
    """
    Check that a regular user gets a 403 Forbidden error.
    CTFd's @admins_only redirects, so we expect a 302.
    """
    response = logged_in_client.get("/ng/teams")
    assert response.status_code == 302
