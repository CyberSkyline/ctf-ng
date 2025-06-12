"""
/backend/ctfd/plugin/tests/api/test_user_api.py
API Tests for user endpoints
"""

import pytest

pytestmark = pytest.mark.db


def test_users_me_teams_endpoint(logged_in_client, team, event):
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
    assert user_team["event_id"] == event.id

    # Check other expected fields
    assert "joined_at" in user_team
    assert "max_team_size" in user_team
    assert "team_member_count" in user_team
