"""
API Tests for user endpoints
"""

import pytest

pytestmark = pytest.mark.db


def test_users_me_teams_endpoint(logged_in_client, team, event):
    """Check that the /me/teams endpoint correctly shows the user's team and its shape."""
    response = logged_in_client.get("/ng/users/me/teams")
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
    assert user_team["event_id"] == event.id

    assert "joined_at" in user_team
    assert "max_team_size" in user_team
    assert "team_member_count" in user_team


def test_get_specific_user_as_admin(admin_client, normal_user):
    """
    Check that an admin can fetch details for a specific user.
    """
    user_id_to_fetch = normal_user.id
    response = admin_client.get(f"/ng/users/{user_id_to_fetch}")
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"]

    user_data = data["data"]["user"]
    assert user_data["id"] == user_id_to_fetch
    assert user_data["name"] == normal_user.name
    assert "team_count" in user_data


def test_get_specific_user_fails_for_normal_user(logged_in_client, admin_user):
    """
    Check that a regular user cannot fetch details for another user.
    """
    user_id_to_fetch = admin_user.id
    response = logged_in_client.get(f"/ng/users/{user_id_to_fetch}")
    assert response.status_code == 302
