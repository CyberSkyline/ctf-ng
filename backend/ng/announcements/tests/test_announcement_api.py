"""
Tests for announcement API endpoints
"""

import pytest
from datetime import (
    UTC,
    datetime,
    timedelta,
)

from CTFd.models import Users, db
from CTFd.cache import cache
from CTFd.utils.security.csrf import generate_nonce

from ..models import (
    Announcement,
    AnnouncementType,
)
from ..services import AnnouncementService
from ...notifications.models import Notification


class TestAnnouncementEndpoints:
    """
    Tests for announcement API endpoints
    """
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

        response = logged_in_client.get("/ng/announcements")

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

        response = logged_in_client.get("/ng/announcements")
        assert response.status_code == 200
        data = response.get_json()

        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == global_announcement.id

        response = logged_in_client.get(
            f"/ng/announcements?event_id={event.id}"
        )
        assert response.status_code == 200
        data = response.get_json()

        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == event_announcement.id

    def test_get_active_announcements_empty(self, logged_in_client):
        """
        Test getting announcements when none exist
        """
        response = logged_in_client.get("/ng/announcements")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == []

    def test_unauthenticated_user_requests_fail(self, client):
        """
        Test that unauthenticated requests fail
        """
        response = client.get("/ng/announcements")
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
            "/ng/admin/announcements/announce",
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
            "/ng/admin/announcements/announce",
            json = {"title": "Test"}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

        response = admin_client.post(
            "/ng/admin/announcements/announce",
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
            "/ng/admin/announcements/announce",
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
            f"/ng/admin/announcements/events/{event.id}/announce",
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
            f"/ng/admin/announcements/events/{event.id}/announce",
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
            "/ng/admin/announcements/events/999999/announce",
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

        response = admin_client.get("/ng/admin/announcements")

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
        response = admin_client.get("/ng/admin/announcements")

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
                "/ng/admin/announcements/announce",
                "POST",
                {
                    "title": "Test",
                    "message": "Test"
                }
            ),
            (
                f"/ng/admin/announcements/events/{event.id}/announce",
                "POST",
                {
                    "title": "Test",
                    "message": "Test"
                }
            ),
            ("/ng/admin/announcements",
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
                "/ng/admin/announcements/announce",
                "POST",
                {
                    "title": "Test",
                    "message": "Test"
                }
            ),
            (
                f"/ng/admin/announcements/events/{event.id}/announce",
                "POST",
                {
                    "title": "Test",
                    "message": "Test"
                }
            ),
            ("/ng/admin/announcements",
             "GET",
             None),
        ]

        for endpoint, method, json_data in endpoints:
            if method == "POST":
                response = client.post(endpoint, json = json_data)
            else:
                response = client.get(endpoint)

            assert response.status_code in [302, 401, 403]

    def test_announcement_flow_end_to_end(
        self,
        app,
        admin,
        user,
        event,
        team_with_member,
        db_session
    ):
        """
        Test complete announcement flow from creation to notification
        """
        announcement = AnnouncementService.send_event_announcement(
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

        # Check that announcement is visible
        announcements_response = user_client.get(
            f"/ng/announcements?event_id={event.id}"
        )
        assert announcements_response.status_code == 200
        announcements = announcements_response.get_json()["data"]
        assert len(announcements) >= 1

        announcement_data = next(
            (a for a in announcements if a["title"] == "Event Starting Soon!"),
            None
        )
        assert announcement_data is not None

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
        global_announcement = AnnouncementService.send_system_announcement(
            title = "Global Maintenance",
            message = "Platform maintenance scheduled",
            sender_id = admin.id
        )
        assert global_announcement is not None

        event_announcement = AnnouncementService.send_event_announcement(
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

        global_response = user_client.get("/ng/announcements")
        assert global_response.status_code == 200
        global_data = global_response.get_json()["data"]
        assert any(a["title"] == "Global Maintenance" for a in global_data)

        event_response = user_client.get(
            f"/ng/announcements?event_id={event.id}"
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
            "/ng/admin/announcements"
        )
        assert admin_all_response.status_code == 200
        admin_data = admin_all_response.get_json()["data"]
        assert len(admin_data) >= 2
        assert any(a["title"] == "Global Maintenance" for a in admin_data)
        assert any(a["title"] == "Event Update" for a in admin_data)

    def test_graceful_handling_of_removed_enum_values_user(
        self,
        logged_in_client,
        announcement_factory,
        db_session
    ):
        """
        Test that announcements with removed/invalid enum values
        are handled gracefully without causing 500 errors
        """
        valid_announcement = announcement_factory(
            type = AnnouncementType.GENERAL,
            title = "Valid Announcement",
            message = "This announcement has a valid type"
        )

        announcement_with_invalid_enum = announcement_factory(
            type = AnnouncementType.EVENT_UPDATE,
            title = "Invalid Enum Announcement",
            message = "This will have an invalid enum value"
        )

        db_session.execute(
            db.text("UPDATE ng_announcements SET type = 'removed_type' WHERE id = :id"),
            {"id": announcement_with_invalid_enum.id}
        )
        db_session.commit()

        response = logged_in_client.get("/ng/announcements")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2

        announcement_types = {a["id"]: a["type"] for a in data["data"]}
        assert announcement_types[valid_announcement.id] == "general"
        assert announcement_types[announcement_with_invalid_enum.id] == "unknown"

    def test_graceful_handling_of_removed_enum_values_admin(
        self,
        admin_client,
        announcement_factory,
        db_session
    ):
        """
        Test that announcements with removed/invalid enum values
        are handled gracefully without causing 500 errors
        """
        valid_announcement = announcement_factory(
            type = AnnouncementType.GENERAL,
            title = "Valid Admin Announcement",
            message = "This announcement has a valid type"
        )

        announcement_with_invalid_enum = announcement_factory(
            type = AnnouncementType.EVENT_UPDATE,
            title = "Invalid Admin Enum Announcement",
            message = "This will have an invalid enum value"
        )

        db_session.execute(
            db.text("UPDATE ng_announcements SET type = 'removed_type' WHERE id = :id"),
            {"id": announcement_with_invalid_enum.id}
        )
        db_session.commit()

        response = admin_client.get("/ng/admin/announcements")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2

        announcement_types = {a["id"]: a["type"] for a in data["data"]}
        assert announcement_types[valid_announcement.id] == "general"
        assert announcement_types[announcement_with_invalid_enum.id] == "unknown"


class TestAnnouncementNotificationFanOut:
    """
    Tests for the notifications an announcement creates
    """
    def test_system_announcement_notifies_disconnected_users(
        self,
        admin_client,
        admin,
        user,
        db_session
    ):
        """
        Test a system announcement notifies users with no live socket
        """
        response = admin_client.post(
            "/ng/admin/announcements/announce",
            json = {
                "title": "Scheduled Maintenance",
                "message": "The platform restarts at 2 AM UTC",
                "send_notification": True
            }
        )

        assert response.status_code == 200
        announcement_id = response.get_json()["data"]["id"]

        recipient_ids = {
            n.recipient_id for n in
            Notification.query.filter_by(announcement_id = announcement_id)
        }
        assert recipient_ids == {
            row.id for row in Users.query.with_entities(Users.id)
        }

    def test_system_announcement_skips_banned_users(
        self,
        admin_client,
        admin,
        user,
        db_session
    ):
        """
        Test a banned user gets no notification
        """
        user.banned = True
        db_session.commit()

        response = admin_client.post(
            "/ng/admin/announcements/announce",
            json = {
                "title": "Scoreboard Frozen",
                "message": "The scoreboard is frozen for the last hour",
                "send_notification": True
            }
        )

        assert response.status_code == 200
        announcement_id = response.get_json()["data"]["id"]

        recipient_ids = {
            n.recipient_id for n in
            Notification.query.filter_by(announcement_id = announcement_id)
        }
        assert recipient_ids == {admin.id}

    def test_event_announcement_links_notifications(
        self,
        admin_client,
        admin,
        team_with_members,
        db_session
    ):
        """
        Test event announcement notifications carry the announcement id
        """
        event_id = team_with_members.event_id

        response = admin_client.post(
            f"/ng/admin/announcements/events/{event_id}/announce",
            json = {
                "title": "New Challenge Released",
                "message": "Check out the new web challenge!",
                "type": "event_update",
                "send_notification": True
            }
        )

        assert response.status_code == 200
        announcement_id = response.get_json()["data"]["id"]

        notifications = Notification.query.filter_by(event_id = event_id).all()
        assert len(notifications) == len(team_with_members.members)
        assert all(
            n.announcement_id == announcement_id for n in notifications
        )


class TestAnnouncementUpdate:
    """
    Tests for updating an announcement
    """
    def test_update_announcement_fields(
        self,
        admin_client,
        announcement_factory
    ):
        """
        Test updating title, message, type and expiration
        """
        announcement = announcement_factory(
            title = "Old title",
            message = "Old message",
            expires_at = None
        )
        expires_at = datetime.now(UTC) + timedelta(days = 1)

        response = admin_client.put(
            f"/ng/admin/announcements/{announcement.id}",
            json = {
                "title": "New title",
                "message": "New message",
                "type": "event_update",
                "expires_at": expires_at.isoformat().replace("+00:00", "Z")
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["title"] == "New title"
        assert data["data"]["message"] == "New message"
        assert data["data"]["type"] == "event_update"

        db.session.refresh(announcement)
        assert announcement.title == "New title"
        assert announcement.type == AnnouncementType.EVENT_UPDATE
        assert announcement.expires_at == expires_at.replace(tzinfo = None)

    def test_update_announcement_syncs_notifications(
        self,
        admin_client,
        admin,
        user,
        db_session
    ):
        """
        Test the update rewrites the title and message of every notification
        """
        create_response = admin_client.post(
            "/ng/admin/announcements/announce",
            json = {
                "title": "Typo in title",
                "message": "Typo in message",
                "send_notification": True
            }
        )
        announcement_id = create_response.get_json()["data"]["id"]

        response = admin_client.put(
            f"/ng/admin/announcements/{announcement_id}",
            json = {
                "title": "Corrected title",
                "message": "Corrected message",
                "type": "general"
            }
        )

        assert response.status_code == 200

        notifications = Notification.query.filter_by(
            announcement_id = announcement_id
        ).all()
        assert len(notifications) > 0
        assert all(n.title == "Corrected title" for n in notifications)
        assert all(n.message == "Corrected message" for n in notifications)

    def test_update_announcement_clears_expiration(
        self,
        admin_client,
        announcement_factory
    ):
        """
        Test an explicit null expiration makes the announcement permanent
        """
        announcement = announcement_factory(
            expires_at = datetime.now(UTC) + timedelta(hours = 1)
        )

        response = admin_client.put(
            f"/ng/admin/announcements/{announcement.id}",
            json = {
                "title": "Permanent",
                "message": "This never expires",
                "type": "general",
                "expires_at": None
            }
        )

        assert response.status_code == 200
        assert response.get_json()["data"]["expires_at"] is None

        db.session.refresh(announcement)
        assert announcement.expires_at is None

    def test_update_announcement_keeps_sender_and_event(
        self,
        admin_client,
        admin,
        event,
        announcement_factory
    ):
        """
        Test an update leaves the sender and the event alone
        """
        announcement = announcement_factory(
            sender_id = admin.id,
            event_id = event.id,
            type = AnnouncementType.EVENT_UPDATE
        )

        response = admin_client.put(
            f"/ng/admin/announcements/{announcement.id}",
            json = {
                "title": "Updated",
                "message": "Updated message",
                "type": "event_end"
            }
        )

        assert response.status_code == 200

        db.session.refresh(announcement)
        assert announcement.sender_id == admin.id
        assert announcement.event_id == event.id

    def test_update_announcement_missing_title(
        self,
        admin_client,
        announcement_factory
    ):
        """
        Test a missing title is rejected and the announcement is unchanged
        """
        announcement_id = announcement_factory(title = "Untouched").id

        response = admin_client.put(
            f"/ng/admin/announcements/{announcement_id}",
            json = {
                "message": "New message",
                "type": "general"
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

        assert Announcement.find_by_id(announcement_id).title == "Untouched"

    def test_update_announcement_invalid_type(
        self,
        admin_client,
        announcement_factory
    ):
        """
        Test an unknown type is rejected
        """
        announcement = announcement_factory()

        response = admin_client.put(
            f"/ng/admin/announcements/{announcement.id}",
            json = {
                "title": "Title",
                "message": "Message",
                "type": "not_a_type"
            }
        )

        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_update_nonexistent_announcement(self, admin_client):
        """
        Test updating an announcement that does not exist
        """
        response = admin_client.put(
            "/ng/admin/announcements/999999",
            json = {
                "title": "Title",
                "message": "Message",
                "type": "general"
            }
        )

        assert response.status_code == 404
        assert response.get_json()["success"] is False

    def test_update_announcement_requires_admin(
        self,
        logged_in_client,
        announcement_factory
    ):
        """
        Test a non admin user cannot update an announcement
        """
        announcement = announcement_factory()

        response = logged_in_client.put(
            f"/ng/admin/announcements/{announcement.id}",
            json = {
                "title": "Title",
                "message": "Message",
                "type": "general"
            }
        )

        assert response.status_code in [302, 403]
