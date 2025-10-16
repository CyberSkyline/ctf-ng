"""
Tests for notification API endpoints
"""

import json
import pytest
from datetime import (
    UTC,
    datetime,
    timedelta,
)
from CTFd.models import db
from CTFd.cache import cache
from CTFd.utils.security.csrf import generate_nonce

from ..models import (
    Notification,
    NotificationType,
)


class TestNotificationEndpoints:
    """
    Tests for user notification API endpoints
    """
    def test_get_my_notifications_basic(
        self,
        logged_in_client,
        user,
        notification_factory,
        db_session
    ):
        """
        Test getting basic user notifications
        """
        notification_factory(
            type = NotificationType.TICKET_CREATE,
            title = "Test Notification 1",
            message = "Your ticket was created",
            recipient_id = user.id
        )
        notification_factory(
            type = NotificationType.TICKET_MESSAGE,
            title = "Test Notification 2",
            message = "You received a ticket reply",
            recipient_id = user.id
        )

        response = logged_in_client.get("/ng/notifications/me")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2

        notification = data["data"][0]
        assert "id" in notification
        assert "type" in notification
        assert "title" in notification
        assert "message" in notification
        assert "read_at" in notification
        assert "created_at" in notification
        assert notification["recipient_id"] == user.id

    def test_get_my_notifications_with_read_filter(
        self,
        logged_in_client,
        user,
        notification_factory,
        db_session
    ):
        """
        Test getting notifications filtered by read status
        """
        unread = notification_factory(
            title = "Unread notification",
            recipient_id = user.id,
            read_at = None
        )

        read = notification_factory(
            title = "Read notification",
            recipient_id = user.id,
            read_at = datetime.now(UTC)
        )

        response = logged_in_client.get("/ng/notifications/me?is_read=false")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == unread.id
        assert data["data"][0]["read_at"] is None

        response = logged_in_client.get("/ng/notifications/me?is_read=true")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == read.id
        assert data["data"][0]["read_at"] is not None

    def test_get_my_notifications_empty(self, logged_in_client):
        """
        Test getting notifications when user has none
        """
        response = logged_in_client.get("/ng/notifications/me")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == []

    def test_get_my_notifications_enriched_data(
        self,
        logged_in_client,
        user,
        admin,
        event,
        team_with_member,
        ticket,
        challenge,
        notification_factory,
        db_session
    ):
        """
        Test that notifications include enriched name data
        """
        notification_factory(
            type = NotificationType.TICKET_MESSAGE,
            title = "Ticket Reply",
            message = "Admin replied to your ticket",
            recipient_id = user.id,
            sender_id = admin.id,
            ticket_id = ticket.id,
            team_id = team_with_member.id,
            event_id = event.id,
            challenge_id = challenge.id
        )

        response = logged_in_client.get("/ng/notifications/me")
        assert response.status_code == 200
        data = response.get_json()

        notification_data = data["data"][0]
        # Check enriched names are included
        assert "sender_name" in notification_data
        assert "ticket_subject" in notification_data
        assert "team_name" in notification_data
        assert "event_name" in notification_data
        assert "challenge_name" in notification_data
        assert notification_data["sender_name"] == admin.name

    def test_get_unread_count_basic(
        self,
        logged_in_client,
        user,
        notification_factory
    ):
        """
        Test getting unread notification count
        """
        notification_factory(recipient_id = user.id, read_at = None)
        notification_factory(recipient_id = user.id, read_at = None)
        notification_factory(
            recipient_id = user.id,
            read_at = datetime.now(UTC)
        )

        response = logged_in_client.get("/ng/notifications/me/unread-count")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["count"] == 2

    def test_get_unread_count_zero(self, logged_in_client, user):
        """
        Test getting unread count when no unread notifications
        """
        response = logged_in_client.get("/ng/notifications/me/unread-count")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["count"] == 0

    def test_get_unread_count_excludes_expired(
        self,
        logged_in_client,
        user,
        notification_factory
    ):
        """
        Test unread count excludes expired notifications
        """

        notification_factory(
            recipient_id = user.id,
            read_at = None,
            expires_at = None
        )

        notification_factory(
            recipient_id = user.id,
            read_at = None,
            expires_at = datetime.now(UTC) - timedelta(hours = 1)
        )

        response = logged_in_client.get("/ng/notifications/me/unread-count")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["count"] == 1

    def test_mark_notification_read_success(
        self,
        logged_in_client,
        user,
        notification_factory,
        db_session
    ):
        """
        Test marking a notification as read
        """
        notification = notification_factory(
            recipient_id = user.id,
            read_at = None
        )

        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/notifications/me/{notification.id}/read",
            data = {"nonce": nonce}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == notification.id
        assert data["data"]["read_at"] is not None

        db_session.refresh(notification)
        assert notification.read_at is not None

    def test_mark_notification_read_already_read(
        self,
        logged_in_client,
        user,
        notification_factory
    ):
        """
        Test marking already read notification as read
        """
        notification = notification_factory(
            recipient_id = user.id,
            read_at = datetime.now(UTC)
        )

        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/notifications/me/{notification.id}/read",
            data = {"nonce": nonce}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_mark_notification_read_not_found(self, logged_in_client):
        """
        Test marking non-existent notification as read
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            "/ng/notifications/me/999999/read",
            data = {"nonce": nonce}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_mark_notification_read_permission_denied(
        self,
        logged_in_client,
        user,
        admin,
        notification_factory
    ):
        """
        Test marking other user's notification as read is denied
        """
        notification = notification_factory(
            recipient_id = admin.id,
            read_at = None
        )

        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/notifications/me/{notification.id}/read",
            data = {"nonce": nonce}
        )

        assert response.status_code == 403

        data = response.get_json()
        if data:
            assert data["success"] is False

    def test_mark_all_read_success(
        self,
        logged_in_client,
        user,
        notification_factory,
        db_session
    ):
        """
        Test marking all notifications as read
        """
        notifications = [
            notification_factory(recipient_id = user.id,
                                 read_at = None),
            notification_factory(recipient_id = user.id,
                                 read_at = None),
            notification_factory(recipient_id = user.id,
                                 read_at = None),
        ]

        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            "/ng/notifications/me/read-all",
            data = {"nonce": nonce}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["count"] == 3

        for notification in notifications:
            db_session.refresh(notification)
            assert notification.read_at is not None

    def test_mark_all_read_empty(self, logged_in_client):
        """
        Test marking all as read when no notifications exist
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            "/ng/notifications/me/read-all",
            data = {"nonce": nonce}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["count"] == 0

    def test_unauthenticated_user_requests_fail(self, client):
        """
        Test that unauthenticated requests fail
        """
        endpoints = [
            "/ng/notifications/me",
            "/ng/notifications/me/unread-count",
            "/ng/notifications/me/1/read",
            "/ng/notifications/me/read-all",
        ]

        for endpoint in endpoints:
            if "/read" in endpoint:
                response = client.post(endpoint)
            else:
                response = client.get(endpoint)
            assert response.status_code in [302, 401, 403]

    def test_notification_flow_end_to_end(
        self,
        app,
        admin,
        user,
        event,
        team_with_member,
        db_session,
        notification_factory
    ):
        """
        Test complete notification flow from creation to reading
        """
        # Create a test notification
        notification_factory(
            type = NotificationType.EVENT_ANNOUNCEMENT,
            title = "Test Notification",
            message = "Event announcement",
            recipient_id = user.id
        )

        cache.clear()

        user_client = app.test_client()
        with user_client.session_transaction() as sess:
            sess.clear()
            sess["id"] = user.id
            sess["name"] = user.name
            sess["type"] = user.type
            sess["nonce"] = generate_nonce()
            sess.permanent = False

        count_response = user_client.get("/ng/notifications/me/unread-count")
        assert count_response.status_code == 200
        assert count_response.get_json()["data"]["count"] >= 1

        notifications_response = user_client.get(
            "/ng/notifications/me?is_read=false"
        )
        assert notifications_response.status_code == 200
        notifications = notifications_response.get_json()["data"]
        assert len(notifications) >= 1

        test_notification = next(
            (n for n in notifications if n["title"] == "Test Notification"),
            None
        )
        assert test_notification is not None

        with user_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        read_response = user_client.post(
            f"/ng/notifications/me/{test_notification['id']}/read",
            data = {"nonce": nonce}
        )
        assert read_response.status_code == 200

        with user_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        read_all_response = user_client.post(
            "/ng/notifications/me/read-all",
            data = {"nonce": nonce}
        )
        assert read_all_response.status_code == 200

        final_count_response = user_client.get(
            "/ng/notifications/me/unread-count"
        )
        assert final_count_response.get_json()["data"]["count"] == 0

    def test_graceful_handling_of_removed_enum_values(
        self,
        logged_in_client,
        user,
        notification_factory,
        db_session
    ):
        """
        Test that notifications with removed/invalid enum values
        are handled gracefully without causing 500 errors
        """
        valid_notification = notification_factory(
            type = NotificationType.TICKET_CREATE,
            title = "Valid Notification",
            message = "This notification has a valid type",
            recipient_id = user.id
        )

        notification_with_invalid_enum = notification_factory(
            type = NotificationType.TICKET_MESSAGE,
            title = "Invalid Enum Notification",
            message = "This will have an invalid enum value",
            recipient_id = user.id
        )

        db_session.execute(
            db.text("UPDATE ng_notifications SET type = 'challenge_released' WHERE id = :id"),
            {"id": notification_with_invalid_enum.id}
        )
        db_session.commit()

        response = logged_in_client.get("/ng/notifications/me")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == valid_notification.id

        count_response = logged_in_client.get("/ng/notifications/me/unread-count")
        assert count_response.status_code == 200
        count_data = count_response.get_json()
        assert count_data["data"]["count"] == 1
