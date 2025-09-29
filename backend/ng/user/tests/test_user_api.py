"""
Tests for user admin routes & user related user routes
"""


def test_get_user_profile(logged_in_client, user):
    """
    Test getting the current user's profile
    """
    response = logged_in_client.get("/ng/users/me")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    user_data = data["data"]
    assert user_data["id"] == user.id
    assert user_data["name"] == user.name
    assert user_data["email"] == user.email
    assert "registered_at" in user_data
    assert "roles" not in user_data


def test_get_user_events(logged_in_client, user, event_factory, team_factory):
    """
    Test getting the current user's events
    """
    event1 = event_factory(name = "User Event 1")
    event2 = event_factory(name = "User Event 2")
    team_factory(event = event1, members = [user])
    team_factory(event = event2, members = [user])

    response = logged_in_client.get("/ng/users/me/events")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    events = data["data"]
    assert len(events) == 2
    event_names = {event["name"] for event in events}
    assert "User Event 1" in event_names
    assert "User Event 2" in event_names

    event_ids = {event["id"] for event in events}
    assert event1.id in event_ids
    assert event2.id in event_ids


def test_get_user_teams(logged_in_client, user, event_factory, team_factory):
    """
    Test getting the current user's teams
    """
    event1 = event_factory(name = "Team Event 1")
    event2 = event_factory(name = "Team Event 2")
    team_factory(event = event1, name = "Team N", members = [user])
    team_factory(event = event2, name = "Team NG", members = [user])

    response = logged_in_client.get("/ng/users/me/teams")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    teams = data["data"]
    assert len(teams) == 2
    team_names = {team["name"] for team in teams}
    assert "Team N" in team_names
    assert "Team NG" in team_names

    for team in teams:
        assert "id" in team
        assert "name" in team
        assert "event_id" in team
        assert team["member_count"] >= 1


def test_admin_get_users(admin_client):
    """
    Test getting all users as an admin
    """
    response = admin_client.get("/ng/admin/users")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["data"] is not None


def test_non_admin_endpoints(logged_in_client, user):
    """
    Test that non-admins cannot access the admin users endpoint
    """
    response = logged_in_client.get("/ng/admin/users")
    assert response.status_code == 403
    response = logged_in_client.get(f"/ng/admin/users/{user.id}")
    assert response.status_code == 403
    response = logged_in_client.put(f"/ng/admin/users/{user.id}", json = {})
    assert response.status_code == 403
    response = logged_in_client.delete(
        "/ng/admin/users/delete",
        json = {"user": user.id}
    )
    assert response.status_code == 403
    response = logged_in_client.get(f"/ng/admin/users/{user.id}/events")
    assert response.status_code == 403
    response = logged_in_client.get(f"/ng/admin/users/{user.id}/teams")
    assert response.status_code == 403


def test_admin_get_user_events(admin_client, user_factory, event_factory, team_factory):
    """
    Test admin getting user events with actual data
    """
    user = user_factory(name = "testuser", email = "test@example.com")
    event = event_factory(name = "Test Event")
    team_factory(event = event, members = [user])

    response = admin_client.get(f"/ng/admin/users/{user.id}/events")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    events = data["data"]
    assert len(events) == 1
    assert events[0]["name"] == "Test Event"
    assert events[0]["id"] == event.id


def test_admin_get_user_teams(admin_client, user_factory, event_factory, team_factory):
    """
    Test admin getting user teams with actual data
    """
    user = user_factory(name = "testuser", email = "test@example.com")
    event = event_factory(name = "Test Event")
    team = team_factory(event = event, name = "Test Team", members = [user])

    response = admin_client.get(f"/ng/admin/users/{user.id}/teams")
    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    teams = data["data"]
    assert len(teams) == 1
    assert teams[0]["name"] == "Test Team"
    assert teams[0]["id"] == team.id
    assert teams[0]["event_id"] == event.id


def test_admin_get_nonexistent_user(admin_client):
    """
    Test admin trying to get a user that doesn't exist
    """
    response = admin_client.get("/ng/admin/users/99999")

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False


def test_admin_update_nonexistent_user(admin_client):
    """
    Test admin trying to update a user that doesn't exist
    """
    response = admin_client.put("/ng/admin/users/99999", json = {"name": "Test"})

    assert response.status_code == 404
    data = response.get_json()

    assert data["success"] is False


def test_get_user(admin_client, user):
    """
    Test getting a specific user as an admin
    """
    response = admin_client.get(f"/ng/admin/users/{user.id}")

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    user_data = data["data"]
    assert user_data["id"] == user.id
    assert user_data["name"] == user.name
    assert user_data["email"] == user.email
    assert "registered_at" in user_data
    assert "roles" in user_data or "role" in user_data


def test_user_put(admin_client, user, db_session):
    """
    Test updating a user as an admin
    """
    updated_data = {"name": "Updated User", "email": "updated@example.com"}
    response = admin_client.put(f"/ng/admin/users/{user.id}", json = updated_data)

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["name"] == updated_data["name"]
    assert data["data"]["email"] == updated_data["email"]

    db_session.refresh(user)
    assert user.name == "Updated User"
    assert user.email == "updated@example.com"

    verify_response = admin_client.get(f"/ng/admin/users/{user.id}")
    verify_data = verify_response.get_json()
    assert verify_data["data"]["name"] == "Updated User"
    assert verify_data["data"]["email"] == "updated@example.com"


def test_delete_user(admin_client, user):
    """
    Test deleting a user as an admin
    """
    user_id = user.id
    response = admin_client.delete(
        "/ng/admin/users/delete",
        json = {"user_id": user_id}
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True

    response = admin_client.get(f"/ng/admin/users/{user_id}")
    assert response.status_code == 404

