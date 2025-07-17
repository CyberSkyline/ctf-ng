import pytest


pytestmark = pytest.mark.db

def test_teamlist(admin_client, event, team_factory,user):
        """Test that the team list endpoint returns the correct data."""
        team = team_factory(event=event,members=[user])
        response = admin_client.get("/ng/admin/teams")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 1
        assert data['data'][0]["id"] == team.id
        assert data['data'][0]["name"] == team.name
        assert data['data'][0]["invite_code"] == team.invite_code


def test_teamdetail(admin_client, event, team_factory,user):
    """Test that the team detail endpoint returns the correct data."""
    team = team_factory(event=event, members=[user])
    response = admin_client.get(f"/ng/admin/teams/{team.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']["id"] == team.id
    assert data['data']["name"] == team.name
    assert data['data']["invite_code"] == team.invite_code

def test_teamdetail_update(admin_client, event, team_factory,user):
    """Test that the team detail endpoint can update a team."""
    team = team_factory(event=event, members=[user])
    new_name = "Updated Team Name"
    response = admin_client.patch(f"/ng/admin/teams/{team.id}", json={"name": new_name})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']

def test_teamdetail_update_invalid_name(admin_client, event, team_factory, user):
    """Test that the team detail endpoint returns an error when trying to update with an invalid name."""
    team = team_factory(event=event, members=[user])
    response = admin_client.patch(f"/ng/admin/teams/{team.id}", json={"name": user.name})
    assert response.status_code == 400
    data = response.get_json()
    assert data['errors']['validation'] == "Team name cannot include a member's name."

def test_teammembers(admin_client, team_with_member):
    """Test that the team members endpoint returns the correct data."""
    team = team_with_member

    response = admin_client.get(f"/ng/admin/teams/{team.id}/members")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) == 1

def test_team_kick(admin_client, team_with_member):
    """Test that the team kick endpoint works correctly."""
    team = team_with_member
    user_id = team.members[0].user_id

    response = admin_client.post(f"/ng/admin/teams/{team.id}/kick", json={"user_id": user_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']

    # Verify that the user is no longer a member of the team
    response = admin_client.get(f"/ng/admin/teams/{team.id}/members")
    assert response.status_code == 200
    members_data = response.get_json()['data']
    assert len(members_data) == 0  # User should be kicked out

def test_team_promote(admin_client, team_with_members):
    """Test that the team promote endpoint works correctly."""
    team = team_with_members
    response = admin_client.post(f"/ng/admin/teams/{team.id}/promote", json={"user_id": team.members[0].user_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']
