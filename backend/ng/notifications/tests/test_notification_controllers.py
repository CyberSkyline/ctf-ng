"""
Tests for notification controllers
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import patch, Mock

from ...core.exceptions import (
    NotFoundError,
    PermissionError,
    ValidationError,
)
from ..controllers import (
    get_my_notifications,
    mark_notification_read,
    mark_all_read,
)
from ..models import (
    Notification,
    NotificationType,
)


class TestGetMyNotifications:
    """
    Test the get_my_notifications controller
    """
    def test_get_notifications_empty(self, db_session, user):
        """
        Test getting notifications for user with no notifications
        """
        result = get_my_notifications(user_id = user.id)

        assert result == []

    def test_get_notifications_basic(self, db_session, user, notification_factory):
        """
        Test getting notifications for user with notifications
        """
        notification1 = notification_factory(
            recipient_id = user.id,
            type = NotificationType.TICKET_CREATE,
            title = "Test Notification 1"
        )
        notification2 = notification_factory(
            recipient_id = user.id,
            type = NotificationType.TICKET_MESSAGE,
            title = "Test Notification 2"
        )

        result = get_my_notifications(user_id = user.id)

        assert len(result) == 2
        assert all(isinstance(n, Notification) for n in result)

        notification_ids = [n.id for n in result]
        assert notification2.id in notification_ids
        assert notification1.id in notification_ids

    def test_get_notifications_filter_read_status(
        self,
        db_session,
        user,
        notification_factory
    ):
        """
        Test filtering notifications by read status
        """
        read_notification = notification_factory(
            recipient_id = user.id,
            read_at = datetime(2023,
                               1,
                               1,
                               tzinfo = UTC),
            title = "Read notification"
        )
        unread_notification = notification_factory(
            recipient_id = user.id,
            read_at = None,
            title = "Unread notification"
        )

        unread_result = get_my_notifications(user_id = user.id, is_read = False)
        assert len(unread_result) == 1
        assert unread_result[0].id == unread_notification.id

        read_result = get_my_notifications(user_id = user.id, is_read = True)
        assert len(read_result) == 1
        assert read_result[0].id == read_notification.id

        all_result = get_my_notifications(user_id = user.id, is_read = None)
        assert len(all_result) == 2

    def test_get_notifications_excludes_other_users(
        self,
        db_session,
        user,
        admin,
        notification_factory
    ):
        """
        Test that notifications from other users are excluded
        """
        user_notification = notification_factory(
            recipient_id = user.id,
            title = "User notification"
        )
        notification_factory(recipient_id = admin.id, title = "Admin notification")

        result = get_my_notifications(user_id = user.id)

        assert len(result) == 1
        assert result[0].id == user_notification.id

    def test_get_notifications_excludes_expired(
        self,
        db_session,
        user,
        notification_factory
    ):
        """
        Test that expired notifications are excluded by default
        """
        active_notification = notification_factory(
            recipient_id = user.id,
            expires_at = None,
            title = "Active notification"
        )
        notification_factory(
            recipient_id = user.id,
            expires_at = datetime(1969,
                                  1,
                                  1,
                                  tzinfo = UTC),
            title = "Expired notification"
        )

        result = get_my_notifications(user_id = user.id)

        assert len(result) == 1
        assert result[0].id == active_notification.id


class TestMarkNotificationRead:
    """
    Test the mark_notification_read controller
    """
    def test_mark_notification_read_success(
        self,
        db_session,
        user,
        notification_factory
    ):
        """
        Test successfully marking a notification as read
        """
        notification = notification_factory(
            recipient_id = user.id,
            read_at = None,
            title = "Unread notification"
        )

        result = mark_notification_read(notification)

        assert isinstance(result, Notification)
        assert result.id == notification.id
        assert result.is_read is True
        assert result.read_at is not None

    def test_mark_notification_read_already_read(
        self,
        db_session,
        user,
        notification_factory
    ):
        """
        Test marking already read notification (should still work)
        """
        read_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo = UTC)
        notification = notification_factory(
            recipient_id = user.id,
            read_at = read_time,
            title = "Already read"
        )

        result = mark_notification_read(notification)

        assert result.read_at == read_time.replace(tzinfo = None)


class TestMarkAllRead:
    """
    Test the mark_all_read controller
    """
    def test_mark_all_read_success(self, db_session, user, notification_factory):
        """
        Test successfully marking all notifications as read
        """
        notification1 = notification_factory(
            recipient_id = user.id,
            read_at = None,
            title = "Unread 1"
        )
        notification2 = notification_factory(
            recipient_id = user.id,
            read_at = None,
            title = "Unread 2"
        )
        notification_factory(
            recipient_id = user.id,
            read_at = datetime(2023,
                               1,
                               1,
                               tzinfo = UTC),
            title = "Already read"
        )

        count = mark_all_read(user_id = user.id)

        assert count == 2

        db_session.refresh(notification1)
        db_session.refresh(notification2)
        assert notification1.is_read is True
        assert notification2.is_read is True

    def test_mark_all_read_empty(self, db_session, user):
        """
        Test marking all read when no unread notifications
        """
        count = mark_all_read(user_id = user.id)

        assert count == 0

    def test_mark_all_read_excludes_other_users(
        self,
        db_session,
        user,
        admin,
        notification_factory
    ):
        """
        Test that mark all read only affects current user
        """
        notification_factory(recipient_id = user.id, read_at = None)
        admin_notification = notification_factory(
            recipient_id = admin.id,
            read_at = None
        )

        count = mark_all_read(user_id = user.id)

        assert count == 1

        db_session.refresh(admin_notification)
        assert admin_notification.is_read is False


class TestControllerIntegration:
    """
    Integration tests for multiple controllers working together
    """
    def test_notification_lifecycle(
        self,
        db_session,
        user,
        admin,
        notification_factory
    ):
        """
        Test complete notification lifecycle
        """
        # 1. Create some notifications
        notification1 = notification_factory(
            recipient_id = user.id,
            read_at = None,
            title = "First"
        )
        notification_factory(
            recipient_id = user.id,
            read_at = None,
            title = "Second"
        )

        # 2. Get unread notifications
        unread_notifications = get_my_notifications(
            user_id = user.id,
            is_read = False
        )
        assert len(unread_notifications) == 2

        # 3. Mark one as read
        mark_notification_read(notification1)

        # 4. Check updated counts
        unread_notifications = get_my_notifications(
            user_id = user.id,
            is_read = False
        )
        read_notifications = get_my_notifications(
            user_id = user.id,
            is_read = True
        )
        assert len(unread_notifications) == 1
        assert len(read_notifications) == 1

        # 5. Mark all remaining as read
        count = mark_all_read(user_id = user.id)
        assert count == 1

        # 6. Verify all are now read
        unread_notifications = get_my_notifications(
            user_id = user.id,
            is_read = False
        )
        read_notifications = get_my_notifications(
            user_id = user.id,
            is_read = True
        )
        assert len(unread_notifications) == 0
        assert len(read_notifications) == 2
