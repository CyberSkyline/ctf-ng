"""
/plugin/tests/test_api.py
API Tests
"""

import pytest
from plugin.team.models.Team import Team
from plugin.team.models.TeamMember import TeamMember
from plugin.team.models.enums import TeamRole

pytestmark = pytest.mark.db


def test_teams_endpoint_requires_authentication(client):
    """Check that teams endpoint requires authentication for anonymous users."""
    response = client.get("/plugin/api/teams?world_id=1")
    assert response.status_code in [302, 403]


def test_teams_endpoint_with_authentication(logged_in_client, world):
    """Check that teams endpoint works for an authenticated user."""
    response = logged_in_client.get(f"/plugin/api/teams?world_id={world.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "teams" in data["data"]


def test_worlds_endpoint_with_authentication(logged_in_client):
    """Check that worlds endpoint works for an authenticated user."""
    response = logged_in_client.get("/plugin/api/worlds")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "worlds" in data["data"]


def test_users_me_teams_endpoint(logged_in_client, team, world):
    """Check that the /me/teams endpoint correctly shows the user's team and its shape."""
    response = logged_in_client.get("/plugin/api/users/me/teams")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]

    assert "teams" in data["data"]
    teams_list = data["data"]["teams"]
    assert isinstance(teams_list, list)
    assert len(teams_list) == 1

    user_team = teams_list[0]
    assert user_team["team_id"] == team.id
    assert user_team["team_name"] == team.name
    assert user_team["world_id"] == world.id
    assert user_team["world_name"] == world.name
    assert "joined_at" in user_team
    assert "team_limit" in user_team


def test_admin_endpoints_require_admin(logged_in_client):
    """Check that a normal user cannot access admin endpoints."""
    response = logged_in_client.get("/plugin/api/admin/stats")
    assert response.status_code in [302, 403]


def test_admin_endpoint_with_admin_user(admin_client):
    """Check that an admin user can access admin endpoints."""
    response = admin_client.get("/plugin/api/admin/stats/counts")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]


def test_create_team_requires_data(logged_in_client):
    """Check that the team creation endpoint validates for missing data."""
    response = logged_in_client.post("/plugin/api/teams", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert not data["success"]
    assert "errors" in data


def test_create_world_is_forbidden_for_normal_user(logged_in_client):
    """
    Confirms: A user with the user role cannot create a world.
    This is a critical security test.
    """
    world_data = {"name": "World By Normal User", "description": "This should fail"}

    response = logged_in_client.post("/plugin/api/worlds", json=world_data)

    # We use in [302, 403]  because CTFd's response can vary. The key is that it's not 2xx.
    assert response.status_code in [302, 403]


def test_create_world_succeeds_for_admin_user(admin_client):
    """
    Confirms: A user with the admin role can create a world.
    This tests the primary success path for the endpoint.
    """
    world_data = {"name": "World By Admin", "description": "This should succeed"}

    response = admin_client.post("/plugin/api/worlds", json=world_data)

    assert response.status_code == 201


def test_create_team_creator_becomes_captain(logged_in_client, world, normal_user):
    """Check that the user who creates a team is automatically made the captain."""
    team_data = {"name": "A New Team", "world_id": world.id}

    response = logged_in_client.post("/plugin/api/teams", json=team_data)
    assert response.status_code == 201
    data = response.get_json()
    team_id = data["data"]["team"]["id"]

    captain_membership = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    assert captain_membership is not None
    assert captain_membership.user_id == normal_user.id


def test_captain_assignment_security(client, team_with_members, admin_user):
    """Check that only the captain or an admin can assign a new captain."""
    from plugin.tests.helpers import login_as

    team_id = team_with_members["team"].id
    captain = team_with_members["captain"]
    member = team_with_members["member"]

    login_as(client, member)
    response = client.post(f"/plugin/api/teams/{team_id}/captain", json={"user_id": member.id})
    assert response.status_code == 403

    login_as(client, captain)
    response = client.post(f"/plugin/api/teams/{team_id}/captain", json={"user_id": member.id})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert data["data"]["captain_id"] == member.id

    new_captain_membership = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    assert new_captain_membership.user_id == member.id

    login_as(client, admin_user)
    response = client.post(f"/plugin/api/teams/{team_id}/captain", json={"user_id": captain.id})
    assert response.status_code == 200


def test_update_team_endpoint_security(client, team_with_members):
    """Check that only the captain or an admin can update team details."""
    from plugin.tests.helpers import login_as

    team_id = team_with_members["team"].id
    captain = team_with_members["captain"]
    member = team_with_members["member"]

    login_as(client, member)
    response = client.patch(f"/plugin/api/teams/{team_id}", json={"name": "Hacked Name"})
    assert response.status_code == 403

    login_as(client, captain)
    response = client.patch(f"/plugin/api/teams/{team_id}", json={"name": "New Captain-Approved Name"})
    assert response.status_code == 200

    db_team = Team.query.get(team_id)
    assert db_team.name == "New Captain-Approved Name"


def test_join_team_fails_if_already_in_a_team_in_world(logged_in_client, admin_client, world, normal_user):
    """
    Confirms a user cannot join a team in a world where they already have a team.
    """

    team_data = {"name": "Another Team", "world_id": world.id}
    response = admin_client.post("/plugin/api/teams", json=team_data)
    assert response.status_code == 201
    team2_id = response.get_json()["data"]["team"]["id"]

    response = logged_in_client.post(f"/plugin/api/teams/{team2_id}/join", json={"world_id": world.id})

    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "errors" in data
    assert "already in team" in data["errors"]["join"].lower()
