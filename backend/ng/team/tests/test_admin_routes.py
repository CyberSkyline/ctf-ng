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
    response = admin_client.put(f"/ng/admin/teams/{team.id}", json={"name": new_name})
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']["name"] == new_name
    assert data['success']

def test_teamdetail_update_invalid_name(admin_client, event, team_factory, user):
    """Test that the team detail endpoint returns an error when trying to update with an invalid name."""
    team = team_factory(event=event, members=[user])
    response = admin_client.put(f"/ng/admin/teams/{team.id}", json={"name": user.name})
    assert response.status_code == 400
    data = response.get_json()
    assert data['errors']['validation'] == "Team name cannot include a member's name."

def test_teamdetail_update_event_timestamps(admin_client, event, team_factory, user):
    """Test that the team detail endpoint can update event timestamps of a team."""
    team = team_factory(event=event, members=[user])
    new_start_timestamp = "2024-01-01T12:00:00Z"
    new_end_time = "2024-12-31T12:00:00Z"
    response = admin_client.put(
        f"/ng/admin/teams/{team.id}",
        json={
            "start_timestamp": new_start_timestamp,
            "end_time": new_end_time
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']["start_timestamp"] == new_start_timestamp
    assert data['data']["end_time"] == new_end_time
    assert data['success']

def test_update_team_ranked_status(admin_client, event, team_factory, user):
    """Test that the team detail endpoint can update the ranked status of a team."""
    team = team_factory(event=event, members=[user], ranked=False)
    response = admin_client.put(f"/ng/admin/teams/{team.id}", json={"ranked": True})
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']["ranked"] is True
    assert data['success']

def test_teammembers(admin_client, team_with_member):
    """Test that the team members endpoint returns the correct data."""
    team = team_with_member

    response = admin_client.get(f"/ng/admin/teams/{team.id}/members")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) == 1

def test_team_kick(admin_client, team_with_members):
    """Test that the team kick endpoint works correctly."""

    team = team_with_members
    user_id = team.members[1].user_id

    response = admin_client.post(f"/ng/admin/teams/{team.id}/kick", json={"user_id": user_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']

    response = admin_client.get(f"/ng/admin/teams/{team.id}/members")
    assert response.status_code == 200
    members_data = response.get_json()['data']
    assert all(member['user_id'] != user_id for member in members_data)

def test_cant_kick_captain(admin_client, team_with_members):
    """Test that kicking the captain when there are other members fails."""
    team = team_with_members
    captain_id = team.members[0].user_id

    response = admin_client.post(f"/ng/admin/teams/{team.id}/kick", json={"user_id": captain_id})
    assert response.status_code == 400
    data = response.get_json()
    assert not data['success']
    assert 'Cannot kick the team captain' in data['errors']['validation']

def team_kick_deletes_team_when_last_member(admin_client, team_with_member):
    """Test that kicking the last member disbands the team."""
    team = team_with_member
    user_id = team.members[0].user_id

    response = admin_client.post(f"/ng/admin/teams/{team.id}/kick", json={"user_id": user_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']

    response = admin_client.get(f"/ng/admin/teams/{team.id}")
    assert response.status_code == 404  # Team should no longer exist

def test_team_promote(admin_client, team_with_members):
    """Test that the team promote endpoint works correctly."""
    team = team_with_members
    response = admin_client.post(f"/ng/admin/teams/{team.id}/promote", json={"user_id": team.members[0].user_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']


def test_admin_teams_list_include_name_enrichment(admin_client, event_factory, team_factory, user_factory):
    """
    Test that admin teams endpoint includes enriched names (event_name)
    """
    event = event_factory(name="Cyber Defense Championship", public=True)
    user = user_factory(name="Team Captain", email="captain@example.com")
    team = team_factory(event=event, members=[user], name="Red Team Alpha")

    response = admin_client.get("/ng/admin/teams")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    team_data = None
    for t in data["data"]:
        if t["id"] == team.id:
            team_data = t
            break

    assert team_data is not None

    # Verify name enrichment is working
    assert "event_name" in team_data
    assert team_data["event_name"] == "Cyber Defense Championship"

    # Verify IDs are still present
    assert team_data["event_id"] == event.id
    assert team_data["name"] == "Red Team Alpha"
