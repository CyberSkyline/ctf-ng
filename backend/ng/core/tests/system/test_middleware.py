"""
Tests for middleware decorators in the CTFd plugin.
/backend/ng/core/testing/system/test_middleware.py
"""

import pytest

# Mark all tests in this file with middleware and db markers (middleware tests need to be isolated)
pytestmark = [pytest.mark.middleware, pytest.mark.db]


def test_user_endpoint_decorator(middleware_client):
    """
    Test the user_endpoint decorator.
    This checks if the decorator correctly applies authentication and JSON validation.
    """
    response = middleware_client.get("/user_decorator_test", query_string={"user_id": 1})

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

def test_admin_endpoint_decorator(middleware_client):
    """
    Test the admin_endpoint decorator.
    This checks if the decorator correctly restricts access to admin users.
    """
    response = middleware_client.get("/admin_decorator_test", query_string={"team_id": 1, "user_id": 1})

    assert response.status_code == 302


def test_loading(middleware_client):
    """
    Test the loading of resources using the middleware decorators.
    This checks if the decorators correctly load user and event data.
    """
    response = middleware_client.post("/loading_model_objects",
        json={
            "user_id": 1,
            "event_id": 1,
            "team_id": 1,
            "invite_code": "fo67ykug",
            "ticket_id": 1,
            "ticket_tag_id": 1
        }
    )
    data = response.get_json()
    assert data["success"] is True
    assert "message" in data
    assert data["message"] == "Loading model objects successful."




def test_get_user_role_permissions(middleware_client):
    """
    Test the get_user_role_permissions middleware decorator.
    This checks if the decorator correctly retrieves user permissions.
    """
    response = middleware_client.get("/get_user_permissions", query_string={"user_id": 1})

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "permissions" in data
    assert isinstance(data["permissions"], list)
    assert len(data["permissions"]) > 0
    assert "CAN_EDIT_TEAM" in data["permissions"]

def test_check_user_can_edit_team(middleware_client):
    """
    Test the check_user_can_edit_team middleware decorator.
    This checks if the decorator correctly verifies if a user can edit a team.
    """
    response = middleware_client.get("/check_user_can_edit_team", query_string={"team_id": 1, "user_id": 1})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "can edit" in data['message']