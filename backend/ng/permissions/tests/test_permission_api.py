import pytest
from ..models.Permission import Permission


pytestmark = pytest.mark.db



def test_get_role_permissions(admin_client, role_with_permissions):
    """Check that we can get permissions for a specific role."""
    role = role_with_permissions
    response = admin_client.get(f"/ng/admin/permissions/{role.id}/details")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "permissions" in data["role"]
    assert len(data["role"]["permissions"]) > 0

def test_role_endpoints_not_authenticated(client, role_with_permissions):
    """Check that role endpoints are not accessible without authentication."""
    role = role_with_permissions
    response = client.get(f"/ng/admin/permissions/{role.id}/details")
    assert response.status_code == 302
    response = client.patch(f"/ng/admin/permissions/{role.id}/details", json={
        "permissions": ["can_edit_team", "can_edit_user"]
    })
    assert response.status_code == 403 

def test_change_role_permissions(admin_client, role_with_permissions):
    """Check that we can change permissions for a specific role."""
    role = role_with_permissions
    response = admin_client.patch(f"/ng/admin/permissions/{role.id}/details", json=
    {
        "permissions": ["CAN_EDIT_TEAM", "CAN_EDIT_USER", "CAN_MANAGE_SUPPORT_TICKETS"]
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "Role" in data["message"]
    assert len(data["role"]["permissions"]) == 3

def test_change_role_invalid_permissions(admin_client, role_with_permissions):
    """Check that we cannot change permissions for a specific role with invalid permissions."""
    role = role_with_permissions
    response = admin_client.patch(f"/ng/admin/permissions/{role.id}/details", json={
        "permissions": ["INVALID_PERMISSION"]
    })
    assert response.status_code == 400
    data = response.get_json()
    assert not data["success"]
    assert "errors" in data
    assert "does not exist" in data["errors"]['role']


def test_get_user_roles(logged_in_client, user_with_roles):
    """Check that we can get roles for a specific user."""
    response = logged_in_client.get(f"/ng/admin/permissions/{user_with_roles.id}/roles")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "roles" in data
    assert len(data["roles"]) > 0

def test_user_endpoints_not_authenticated(client, user_with_roles):
    """Check that user endpoints are not accessible without authentication."""
    response = client.get(f"/ng/admin/permissions/{user_with_roles.id}/roles")
    assert response.status_code == 302
    response = client.patch(f"/ng/admin/permissions/{user_with_roles.id}/roles", json={
        "roles": ["Test Role"]
    })
    assert response.status_code == 403

def test_update_user_roles(admin_client, user_with_roles):
    """Check that we can update roles for a specific user."""
    response = admin_client.patch(f"/ng/admin/permissions/{user_with_roles.id}/roles", json={
        "roles": ["admin"]
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "message" in data
    assert data["message"] == "User roles updated successfully"
    assert "admin" in data["user"]["roles"]

def test_update_user_roles_invalid_role(admin_client, user_with_roles):
    """Check that we cannot update roles for a specific user with an invalid role."""
    response = admin_client.patch(f"/ng/admin/permissions/{user_with_roles.id}/roles", json={
        "roles": ["Invalid Role"]
    })
    assert response.status_code == 400
    data = response.get_json()
    assert not data["success"]
    assert "errors" in data
    assert "Invalid" in data["errors"]['user']


