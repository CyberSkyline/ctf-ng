"""
Tests for user ban/unban functionality
"""


def test_admin_ban_user(admin_client, user_factory, db_session):
    """
    Test that an admin can ban a user
    """
    user = user_factory(
        name = "bannable_user",
        email = "banme@example.com"
    )

    response = admin_client.post(
        f"/ng/admin/users/{user.id}/ban",
        json = {}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    db_session.refresh(user.ctfd_user)
    assert user.ctfd_user.banned is True


def test_admin_unban_user(admin_client, user_factory, db_session):
    """
    Test that an admin can unban a user
    """
    user = user_factory(
        name = "banned_user",
        email = "banned@example.com"
    )
    user.ctfd_user.banned = True
    db_session.commit()

    response = admin_client.post(
        f"/ng/admin/users/{user.id}/unban",
        json = {}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    db_session.refresh(user.ctfd_user)
    assert user.ctfd_user.banned is False


def test_banned_user_cannot_login(
    logged_in_client,
    user_factory,
    db_session
):
    """
    Test that a banned user cannot login
    """
    user = user_factory(
        name = "banned_login_user",
        email = "bannedlogin@example.com"
    )
    user.ctfd_user.banned = True
    db_session.commit()

    response = logged_in_client.post(
        "/ng/users/login",
        json = {
            "username": "banned_login_user",
            "password": "password"
        }
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert "banned" in data["errors"]["authentication"].lower()


def test_non_admin_cannot_ban_user(logged_in_client, user_factory):
    """
    Test that a non admin user cannot ban another user
    """
    target_user = user_factory(
        name = "target_user",
        email = "target@example.com"
    )

    response = logged_in_client.post(
        f"/ng/admin/users/{target_user.id}/ban",
        json = {}
    )

    assert response.status_code == 403
