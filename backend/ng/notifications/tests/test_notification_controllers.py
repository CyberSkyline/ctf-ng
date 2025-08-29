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
from ..controllers.user_actions import (
        get_my_notifications,
        mark_notification_read,
        mark_all_read,
        )
from ..controllers.admin_actions import (
        send_announcement,
        send_event_announcement,
        get_all_announcements,
        )
from ..controllers.all_actions import (
        get_active_announcements,
        )
from ..models import (
        Notification,
        NotificationType,
        Announcement,
        AnnouncementType,
        )
from ..services import NotificationService


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

    def test_get_notifications_basic(
            self,
            db_session,
            user,
            notification_factory
            ):
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
        notification_factory(
                recipient_id = admin.id,
                title = "Admin notification"
                )

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

        result = mark_notification_read(
                notification_id = notification.id,
                user_id = user.id
                )

        assert isinstance(result, Notification)
        assert result.id == notification.id
        assert result.is_read is True
        assert result.read_at is not None

    def test_mark_notification_read_not_found(self, db_session, user):
        """
        Test marking non-existent notification fails
        """
        with pytest.raises(NotFoundError) as exc_info:
            mark_notification_read(notification_id = 99999, user_id = user.id)

        assert "Notification 99999 not found" in str(exc_info.value)

    def test_mark_notification_read_permission_denied(
            self,
            db_session,
            user,
            admin,
            notification_factory
            ):
        """
        Test marking other user's notification fails
        """
        notification = notification_factory(
                recipient_id = admin.id,
                read_at = None,
                title = "Admin's notification"
                )

        with pytest.raises(PermissionError) as exc_info:
            mark_notification_read(
                    notification_id = notification.id,
                    user_id = user.id
                    )

        assert "cannot mark other users' notifications" in str(exc_info.value)

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

        result = mark_notification_read(
                notification_id = notification.id,
                user_id = user.id
                )

        assert result.read_at == read_time.replace(tzinfo = None)


class TestMarkAllRead:
    """
    Test the mark_all_read controller
    """
    def test_mark_all_read_success(
            self,
            db_session,
            user,
            notification_factory
            ):
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


class TestSendAnnouncement:
    """
    Test the send_announcement controller
    """
    @patch.object(NotificationService, 'send_system_announcement')
    def test_send_announcement_success(
            self,
            mock_send_system,
            db_session,
            admin,
            announcement_factory
            ):
        """
        Test successfully sending system announcement
        """
        mock_announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                title = "Test Announcement",
                sender_id = admin.id
                )
        mock_send_system.return_value = mock_announcement

        result = send_announcement(
                title = "Test Announcement",
                message = "Test message",
                sender_id = admin.id
                )

        mock_send_system.assert_called_once_with(
                title = "Test Announcement",
                message = "Test message",
                sender_id = admin.id,
                persist = True
                )
        assert result == mock_announcement

    @patch.object(NotificationService, 'send_system_announcement')
    def test_send_announcement_no_sender(self, mock_send_system, db_session):
        """
        Test sending announcement without sender
        """
        mock_send_system.return_value = None

        result = send_announcement(
                title = "System Announcement",
                message = "Automated message",
                sender_id = None
                )

        mock_send_system.assert_called_once_with(
                title = "System Announcement",
                message = "Automated message",
                sender_id = None,
                persist = True
                )
        assert result is None


class TestSendEventAnnouncement:
    """
    Test the send_event_announcement controller
    """
    @patch.object(NotificationService, 'send_event_announcement')
    def test_send_event_announcement_success(
            self,
            mock_send_event,
            db_session,
            admin,
            event,
            announcement_factory
            ):
        """
        Test successfully sending event announcement
        """
        mock_announcement = announcement_factory(
                type = AnnouncementType.EVENT_START,
                title = "Event Starting",
                event_id = event.id
                )
        mock_send_event.return_value = mock_announcement

        result = send_event_announcement(
                event_id = event.id,
                title = "Event Starting",
                message = "The event will begin soon",
                announcement_type = "event_start",
                sender_id = admin.id
                )

        mock_send_event.assert_called_once_with(
                event_id = event.id,
                announcement_type = AnnouncementType.EVENT_START,
                title = "Event Starting",
                message = "The event will begin soon",
                sender_id = admin.id
                )
        assert result == mock_announcement

    def test_send_event_announcement_invalid_type(
            self,
            db_session,
            admin,
            event
            ):
        """
        Test sending event announcement with invalid type fails
        """
        with pytest.raises(ValidationError) as exc_info:
            send_event_announcement(
                    event_id = event.id,
                    title = "Test",
                    message = "Test message",
                    announcement_type = "invalid_type",
                    sender_id = admin.id
                    )

        assert "Invalid announcement type: invalid_type" in str(exc_info.value)

    @patch.object(NotificationService, 'send_event_announcement')
    def test_send_event_announcement_valid_types(
            self,
            mock_send_event,
            db_session,
            admin,
            event
            ):
        """
        Test all valid announcement types work
        """
        valid_types = [
                "general",
                "event_update",
                "event_start",
                "event_end",
                "leaderboard_update"
                ]

        for announcement_type in valid_types:
            mock_send_event.return_value = Mock()

            result = send_event_announcement(
                    event_id = event.id,
                    title = "Test",
                    message = "Test message",
                    announcement_type = announcement_type,
                    sender_id = admin.id
                    )

            assert result is not None


class TestGetAllAnnouncements:
    """
    Test the get_all_announcements controller
    """
    @patch.object(Announcement, 'get_all_announcements')
    def test_get_all_announcements_success(self, mock_get_all, db_session):
        """
        Test getting all announcements
        """
        mock_announcements = [Mock(), Mock(), Mock()]
        mock_get_all.return_value = mock_announcements

        result = get_all_announcements()

        mock_get_all.assert_called_once()
        assert result == mock_announcements

    def test_get_all_announcements_empty(self, db_session):
        """
        Test getting all announcements when none exist
        """
        result = get_all_announcements()

        assert result == []

    def test_get_all_announcements_with_data(
            self,
            db_session,
            announcement_factory
            ):
        """
        Test getting all announcements with real data
        """
        announcement1 = announcement_factory(
                type = AnnouncementType.GENERAL,
                title = "First announcement"
                )
        announcement2 = announcement_factory(
                type = AnnouncementType.EVENT_UPDATE,
                title = "Second announcement"
                )

        result = get_all_announcements()

        assert len(result) >= 2
        announcement_ids = [a.id for a in result]
        assert announcement1.id in announcement_ids
        assert announcement2.id in announcement_ids


class TestGetActiveAnnouncements:
    """
    Test the get_active_announcements controller
    """
    @patch.object(Announcement, 'get_active_announcements')
    def test_get_active_announcements_global(self, mock_get_active, db_session):
        """
        Test getting active global announcements
        """
        mock_announcements = [Mock(), Mock()]
        mock_get_active.return_value = mock_announcements

        result = get_active_announcements()

        mock_get_active.assert_called_once_with(event_id = None)
        assert result == mock_announcements

    @patch.object(Announcement, 'get_active_announcements')
    def test_get_active_announcements_event_specific(
            self,
            mock_get_active,
            db_session,
            event
            ):
        """
        Test getting active event-specific announcements
        """
        mock_announcements = [Mock()]
        mock_get_active.return_value = mock_announcements

        result = get_active_announcements(event_id = event.id)

        mock_get_active.assert_called_once_with(
                event_id = event.id
                )
        assert result == mock_announcements

    def test_get_active_announcements_with_data(
            self,
            db_session,
            announcement_factory,
            event
            ):
        """
        Test getting active announcements with real data
        """
        global_announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                event_id = None,
                expires_at = None,
                title = "Global announcement"
                )

        event_announcement = announcement_factory(
                type = AnnouncementType.EVENT_UPDATE,
                event_id = event.id,
                expires_at = None,
                title = "Event announcement"
                )

        announcement_factory(
                type = AnnouncementType.GENERAL,
                event_id = None,
                expires_at = datetime(1969,
                                      1,
                                      1,
                                      tzinfo = UTC),
                title = "Expired announcement"
                )

        global_result = get_active_announcements()
        global_ids = [a.id for a in global_result]
        assert global_announcement.id in global_ids
        assert event_announcement.id not in global_ids

        event_result = get_active_announcements(event_id = event.id)
        event_ids = [a.id for a in event_result]
        assert event_announcement.id in event_ids
        assert global_announcement.id not in event_ids


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
        mark_notification_read(
                notification_id = notification1.id,
                user_id = user.id
                )

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

    @patch.object(NotificationService, 'send_system_announcement')
    @patch.object(NotificationService, 'send_event_announcement')
    def test_announcement_workflow(
            self,
            mock_send_event,
            mock_send_system,
            db_session,
            admin,
            event
            ):
        """
        Test complete announcement workflow
        """
        # Mock return values
        mock_system_announcement = Mock()
        mock_event_announcement = Mock()
        mock_send_system.return_value = mock_system_announcement
        mock_send_event.return_value = mock_event_announcement

        # 1. Send system announcement
        system_result = send_announcement(
                title = "System Maintenance",
                message = "Scheduled maintenance tonight",
                sender_id = admin.id
                )
        assert system_result == mock_system_announcement

        # 2. Send event announcement
        event_result = send_event_announcement(
                event_id = event.id,
                title = "Event Starting",
                message = "Get ready!",
                announcement_type = "event_start",
                sender_id = admin.id
                )
        assert event_result == mock_event_announcement

        # 3. Verify service calls
        mock_send_system.assert_called_once_with(
                title = "System Maintenance",
                message = "Scheduled maintenance tonight",
                sender_id = admin.id,
                persist = True
                )
        mock_send_event.assert_called_once_with(
                event_id = event.id,
                announcement_type = AnnouncementType.EVENT_START,
                title = "Event Starting",
                message = "Get ready!",
                sender_id = admin.id
                )
