

def test_get_user_profile(logged_in_client):
    """Test getting the current user's profile."""
    response = logged_in_client.get("/ng/users/me")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

def test_get_user_events(logged_in_client):
    """Test getting the current user's events."""
    response = logged_in_client.get("/ng/users/me/events")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

def test_get_user_teams(logged_in_client):
    """Test getting the current user's teams."""
    response = logged_in_client.get("/ng/users/me/teams")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

def test_admin_get_users(admin_client):
    """Test getting all users as an admin."""
    response = admin_client.get("/ng/admin/users")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"] is not None

def test_non_admin_endpoints(logged_in_client, event_factory, team_factory,user):
    """Test that non-admins cannot access the admin users endpoint."""
    event = event_factory()
    team = team_factory(members=[user])
    response = logged_in_client.get("/ng/admin/users")
    assert response.status_code == 302
    response = logged_in_client.get(f"/ng/admin/users/{user.id}")
    assert response.status_code == 302
    response = logged_in_client.put(f"/ng/admin/users/{user.id}", json={})
    assert response.status_code == 403
    response = logged_in_client.delete(f"/ng/admin/users/delete", json={"user": user.id})
    assert response.status_code == 403
    response = logged_in_client.get(f"/ng/admin/users/{user.id}/events")
    assert response.status_code == 302
    response = logged_in_client.get(f"/ng/admin/users/{user.id}/teams")
    assert response.status_code == 302

def test_get_user(admin_client, user):
    """Test getting a specific user as an admin."""
    response = admin_client.get(f"/ng/admin/users/{user.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["id"] == user.id


def test_user_put(admin_client, user):
    """Test updating a user as an admin."""
    updated_data = {
        "name": "Updated User",
        "email": "updated@example.com"
    }
    response = admin_client.put(f"/ng/admin/users/{user.id}", json=updated_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == updated_data["name"]

def test_delete_user(admin_client, user):
    """Test deleting a user as an admin."""
    response = admin_client.delete(f"/ng/admin/users/delete",json={"user_id": user.id})
    print(response.get_json())
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    response = admin_client.get(f"/ng/admin/users/{user.id}")
    assert response.status_code == 404  # User should no longer exist
