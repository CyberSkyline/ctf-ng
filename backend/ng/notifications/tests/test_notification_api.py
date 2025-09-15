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

from CTFd.cache import cache
from CTFd.utils.security.csrf import generate_nonce

from ..models import (
    Notification,
    NotificationType,
    Announcement,
    AnnouncementType,
)
from ..services import NotificationService


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
            type = NotificationType.TEAM_INVITATION,
            title = "Test Notification 2",
            message = "You were invited to a team",
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

    def test_get_active_announcements_basic(
        self,
        logged_in_client,
        announcement_factory
    ):
        """
        Test getting active announcements
        """
        active = announcement_factory(
            type = AnnouncementType.GENERAL,
            title = "Active announcement",
            expires_at = None
        )

        announcement_factory(
            title = "Expired announcement",
            expires_at = datetime.now(UTC) - timedelta(hours = 1)
        )

        response = logged_in_client.get("/ng/notifications/announcements")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == active.id
        assert data["data"][0]["title"] == "Active announcement"

    def test_get_active_announcements_event_filter(
        self,
        logged_in_client,
        event,
        announcement_factory
    ):
        """
        Test getting announcements filtered by event
        """
        global_announcement = announcement_factory(
            title = "Global announcement",
            event_id = None
        )

        event_announcement = announcement_factory(
            title = "Event announcement",
            event_id = event.id
        )

        response = logged_in_client.get("/ng/notifications/announcements")
        assert response.status_code == 200
        data = response.get_json()

        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == global_announcement.id

        response = logged_in_client.get(
            f"/ng/notifications/announcements?event_id={event.id}"
        )
        assert response.status_code == 200
        data = response.get_json()

        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == event_announcement.id

    def test_get_active_announcements_empty(self, logged_in_client):
        """
        Test getting announcements when none exist
        """
        response = logged_in_client.get("/ng/notifications/announcements")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == []

    def test_unauthenticated_user_requests_fail(self, client):
        """
        Test that unauthenticated requests fail
        """
        endpoints = [
            "/ng/notifications/me",
            "/ng/notifications/me/unread-count",
            "/ng/notifications/me/1/read",
            "/ng/notifications/me/read-all",
            "/ng/notifications/announcements",
        ]

        for endpoint in endpoints:
            if "/read" in endpoint:
                response = client.post(endpoint)
            else:
                response = client.get(endpoint)
            assert response.status_code in [302, 401, 403]

    def test_send_system_announcement_success(
        self,
        admin_client,
        admin,
        db_session
    ):
        """
        Test sending system-wide announcement
        """
        response = admin_client.post(
            "/ng/admin/notifications/announce",
            json = {
                "title": "System Maintenance",
                "message":
                "System will be down for maintenance from 2-4 PM UTC"
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["title"] == "System Maintenance"
        assert data["data"]["sender_id"] == admin.id

    def test_send_system_announcement_missing_fields(self, admin_client):
        """
        Test sending announcement with missing required fields
        """
        response = admin_client.post(
            "/ng/admin/notifications/announce",
            json = {"title": "Test"}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

        response = admin_client.post(
            "/ng/admin/notifications/announce",
            json = {"message": "Test message"}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_send_system_announcement_empty_fields(self, admin_client):
        """
        Test sending announcement with empty fields
        """
        response = admin_client.post(
            "/ng/admin/notifications/announce",
            json = {
                "title": "   ",
                "message": "Valid message"
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_send_event_announcement_success(
        self,
        admin_client,
        admin,
        event,
        user,
        team_with_member,
        db_session
    ):
        """
        Test sending event-specific announcement
        """
        response = admin_client.post(
            f"/ng/admin/notifications/events/{event.id}/announce",
            json = {
                "title": "New Challenge Released",
                "message": "Check out the new web challenge!",
                "type": "event_update"
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["title"] == "New Challenge Released"
        assert data["data"]["event_id"] == event.id
        assert data["data"]["sender_id"] == admin.id

    def test_send_event_announcement_invalid_type(self, admin_client, event):
        """
        Test sending event announcement with invalid type
        """
        response = admin_client.post(
            f"/ng/admin/notifications/events/{event.id}/announce",
            json = {
                "title": "Test",
                "message": "Test message",
                "type": "invalid_type"
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_send_event_announcement_nonexistent_event(self, admin_client):
        """
        Test sending announcement to non existent event
        """
        response = admin_client.post(
            "/ng/admin/notifications/events/999999/announce",
            json = {
                "title": "Test",
                "message": "Test message"
            }
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_get_all_announcements_admin(
        self,
        admin_client,
        announcement_factory
    ):
        """
        Test admin getting all announcements (including expired)
        """
        active = announcement_factory(
            title = "Active announcement",
            expires_at = None
        )

        expired = announcement_factory(
            title = "Expired announcement",
            expires_at = datetime.now(UTC) - timedelta(hours = 1)
        )

        response = admin_client.get("/ng/admin/notifications/announcements")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2

        announcement_ids = [a["id"] for a in data["data"]]
        assert active.id in announcement_ids
        assert expired.id in announcement_ids

    def test_get_all_announcements_empty(self, admin_client):
        """
        Test getting all announcements when none exist
        """
        response = admin_client.get("/ng/admin/notifications/announcements")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == []

    def test_admin_endpoints_require_admin_auth(self, logged_in_client, event):
        """
        Test that admin endpoints require admin privileges
        """
        endpoints = [
            (
                "/ng/admin/notifications/announce",
                "POST",
                {
                    "title": "Test",
                    "message": "Test"
                }
            ),
            (
                f"/ng/admin/notifications/events/{event.id}/announce",
                "POST",
                {
                    "title": "Test",
                    "message": "Test"
                }
            ),
            ("/ng/admin/notifications/announcements",
             "GET",
             None),
        ]

        for endpoint, method, json_data in endpoints:
            if method == "POST":
                response = logged_in_client.post(endpoint, json = json_data)
            else:
                response = logged_in_client.get(endpoint)

            assert response.status_code in [302, 403]

    def test_unauthenticated_admin_requests_fail(self, client, event):
        """
        Test that unauthenticated admin requests fail
        """
        endpoints = [
            (
                "/ng/admin/notifications/announce",
                "POST",
                {
                    "title": "Test",
                    "message": "Test"
                }
            ),
            (
                f"/ng/admin/notifications/events/{event.id}/announce",
                "POST",
                {
                    "title": "Test",
                    "message": "Test"
                }
            ),
            ("/ng/admin/notifications/announcements",
             "GET",
             None),
        ]

        for endpoint, method, json_data in endpoints:
            if method == "POST":
                response = client.post(endpoint, json = json_data)
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
        announcement = NotificationService.send_event_announcement(
            event_id = event.id,
            announcement_type = AnnouncementType.EVENT_START,
            title = "Event Starting Soon!",
            message = "The event will begin in 15 minutes",
            sender_id = admin.id
        )
        assert announcement is not None

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

        announcement_notification = next(
            (n for n in notifications if n["title"] == "Event Starting Soon!"),
            None
        )
        assert announcement_notification is not None

        with user_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        read_response = user_client.post(
            f"/ng/notifications/me/{announcement_notification['id']}/read",
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

    def test_announcement_visibility_scoping(
        self,
        app,
        admin,
        user,
        event,
        db_session
    ):
        """
        Test that announcement visibility is properly scoped
        """
        global_announcement = NotificationService.send_system_announcement(
            title = "Global Maintenance",
            message = "Platform maintenance scheduled",
            sender_id = admin.id
        )
        assert global_announcement is not None

        event_announcement = NotificationService.send_event_announcement(
            event_id = event.id,
            announcement_type = AnnouncementType.EVENT_UPDATE,
            title = "Event Update",
            message = "New challenge added",
            sender_id = admin.id
        )
        assert event_announcement is not None

        cache.clear()

        user_client = app.test_client()
        with user_client.session_transaction() as sess:
            sess.clear()
            sess["id"] = user.id
            sess["name"] = user.name
            sess["type"] = user.type
            sess["nonce"] = generate_nonce()
            sess.permanent = False

        global_response = user_client.get("/ng/notifications/announcements")
        assert global_response.status_code == 200
        global_data = global_response.get_json()["data"]
        assert any(a["title"] == "Global Maintenance" for a in global_data)

        event_response = user_client.get(
            f"/ng/notifications/announcements?event_id={event.id}"
        )
        assert event_response.status_code == 200
        event_data = event_response.get_json()["data"]
        assert any(a["title"] == "Event Update" for a in event_data)

        admin_client = app.test_client()
        with admin_client.session_transaction() as sess:
            sess.clear()
            sess["id"] = admin.id
            sess["name"] = admin.name
            sess["type"] = admin.type
            sess["nonce"] = generate_nonce()
            sess.permanent = False

        admin_all_response = admin_client.get(
            "/ng/admin/notifications/announcements"
        )
        assert admin_all_response.status_code == 200
        admin_data = admin_all_response.get_json()["data"]
        assert len(admin_data) >= 2
        assert any(a["title"] == "Global Maintenance" for a in admin_data)
        assert any(a["title"] == "Event Update" for a in admin_data)
