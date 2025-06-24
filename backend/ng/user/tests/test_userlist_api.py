"""
Extended API Tests for user endpoints, covering admin actions.
/backend/ng/user/tests/test_user_api_extended.py
"""

import pytest
from tests.helpers import gen_user
from CTFd.models import db as _db

pytestmark = pytest.mark.db


def test_list_all_users_as_admin(admin_client, db_session):
    """
    Test that an admin can successfully fetch the list of all users.
    """

    from ...user.models.User import User as NgUser

    for i in range(3):
        ctfd_user = gen_user(_db, name=f"test_user_{i}", email=f"test{i}@example.com")
        ng_user = NgUser(id=ctfd_user.id)
        db_session.add(ng_user)
    db_session.commit()

    response = admin_client.get("/ng/users/all")
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert "users" in data["data"]
    assert "total" in data["data"]

    users_list = data["data"]["users"]

    assert len(users_list) >= 4
    assert data["data"]["total"] == len(users_list)

    first_user = users_list[0]
    assert "id" in first_user
    assert "name" in first_user
    assert "email" in first_user
    assert "role" in first_user
    assert "registered_at" in first_user
    assert "team_count" in first_user

    admin_in_list = any(user["role"] == "admin" for user in users_list)
    assert admin_in_list is True


def test_list_all_users_fails_for_normal_user(logged_in_client):
    """
    Test that a regular, non-admin user cannot access the list of all users.
    """

    response = logged_in_client.get("/ng/users/all")

    assert response.status_code == 302
    assert response.location is not None


def test_list_all_users_fails_for_anonymous_user(client, db_session):
    """
    Test that an unauthenticated user cannot access the list of all users.
    """

    response = client.get("/ng/users/all")

    assert response.status_code == 302
    assert response.location is not None
