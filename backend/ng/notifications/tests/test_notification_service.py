"""
Tests for NotificationService - covering both stored notifications and WebSocket events
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import patch, Mock, call

from ..services.notification_service import NotificationService
from ..models import (
    Notification,
    NotificationType,
    Announcement,
    AnnouncementType,
)
from ...core.utils import emit_event


class TestNotificationServiceEmitters:
    """
    Test the private emitter methods
    """
    @patch('ng.notifications.services.notification_service.emit_event')
    def test_emit_refetch(self, mock_emit):
        """
        Test _emit_refetch sends correct WebSocket event
        """
        NotificationService._emit_refetch("/api/test", "test_room")

        mock_emit.assert_called_once_with(
            event_name = "refetch",
            data = {"path": "/api/test"},
            room = "test_room"
        )

    @patch('ng.notifications.services.notification_service.emit_event')
    def test_emit_refetch_no_room(self, mock_emit):
        """
        Test _emit_refetch without room broadcasts to all
        """
        NotificationService._emit_refetch("/api/global")

        mock_emit.assert_called_once_with(
            event_name = "refetch",
            data = {"path": "/api/global"},
            room = None
        )

    @patch('ng.notifications.services.notification_service.emit_event')
    def test_emit_notification(self, mock_emit, notification_factory, user):
        """
        Test _emit_notification sends notification to correct room
        """
        notification = notification_factory(
            recipient_id = user.id,
            title = "Test Notification"
        )

        NotificationService._emit_notification(notification)

        mock_emit.assert_called_once_with(
            event_name = "notification",
            data = notification.serialize(),
            room = f"user_{user.id}"
        )


class TestTicketNotifications:
    """
    Test ticket related notifications (stored + WebSocket)
    """
    @patch.object(NotificationService, '_emit_notification')
    @patch.object(NotificationService, '_emit_refetch')
    @patch.object(Notification, 'create_notification')
    def test_notify_ticket_reply_admin_to_user(
        self,
        mock_create,
        mock_emit_refetch,
        mock_emit_notification
    ):
        """Test admin replying to user ticket"""
        mock_notification = Mock()
        mock_create.return_value = mock_notification

        NotificationService.notify_ticket_reply(
            ticket_id = 123,
            author_id = 2,  # admin
            recipient_id = 1,  # user
            is_admin_reply = True
        )

        mock_create.assert_called_once_with(
            notification_type = NotificationType.TICKET_MESSAGE,
            title = "Support Ticket Update",
            message = "Admin replied to your ticket",
            recipient_id = 1,
            sender_id = 2,
            ticket_id = 123
        )

        mock_emit_notification.assert_called_once_with(mock_notification)

        mock_emit_refetch.assert_called_once_with(
            path = "/ng/support/tickets/123",
            room = "ticket_123"
        )

    @patch.object(NotificationService, '_emit_notification')
    @patch.object(NotificationService, '_emit_refetch')
    @patch.object(Notification, 'create_notification')
    def test_notify_ticket_reply_user_to_admin(
        self,
        mock_create,
        mock_emit_refetch,
        mock_emit_notification
    ):
        """
        Test user replying to admin
        """
        mock_notification = Mock()
        mock_create.return_value = mock_notification

        NotificationService.notify_ticket_reply(
            ticket_id = 456,
            author_id = 1,  # user
            recipient_id = 2,  # admin
            is_admin_reply = False
        )

        mock_create.assert_called_once_with(
            notification_type = NotificationType.TICKET_MESSAGE,
            title = "Support Ticket Update",
            message = "User replied to your ticket",
            recipient_id = 2,
            sender_id = 1,
            ticket_id = 456
        )

        mock_emit_notification.assert_called_once_with(mock_notification)
        mock_emit_refetch.assert_called_once_with(
            path = "/ng/support/tickets/456",
            room = "ticket_456"
        )

    @patch.object(NotificationService, '_emit_notification')
    @patch.object(NotificationService, '_emit_refetch')
    @patch.object(Notification, 'create_notification')
    def test_notify_ticket_status_change(
        self,
        mock_create,
        mock_emit_refetch,
        mock_emit_notification
    ):
        """
        Test ticket status change notification
        """
        mock_notification = Mock()
        mock_create.return_value = mock_notification

        NotificationService.notify_ticket_status_change(
            ticket_id = 789,
            recipient_id = 1,
            new_status = "closed",
            changed_by_id = 2
        )

        mock_create.assert_called_once_with(
            notification_type = NotificationType.TICKET_STATUS_CHANGE,
            title = "Ticket Status Changed",
            message = "Your ticket was closed",
            recipient_id = 1,
            sender_id = 2,
            ticket_id = 789
        )

        mock_emit_notification.assert_called_once_with(mock_notification)
        mock_emit_refetch.assert_called_once_with(
            path = "/ng/support/tickets/789",
            room = "ticket_789"
        )

    @patch.object(NotificationService, '_emit_notification')
    @patch.object(Notification, 'create_notification')
    def test_notify_ticket_assigned(self, mock_create, mock_emit_notification):
        """
        Test ticket assignment notification (no refetch needed)
        """
        mock_notification = Mock()
        mock_create.return_value = mock_notification

        NotificationService.notify_ticket_assigned(
            ticket_id = 101,
            assigned_to_id = 2,
            assigned_by_id = 3
        )

        mock_create.assert_called_once_with(
            notification_type = NotificationType.TICKET_ASSIGNED,
            title = "Ticket Assigned",
            message = "A support ticket has been assigned to you",
            recipient_id = 2,
            sender_id = 3,
            ticket_id = 101
        )

        mock_emit_notification.assert_called_once_with(mock_notification)


class TestScoringBroadcasts:
    """
    Test scoring updates
    """
    @patch.object(NotificationService, '_emit_refetch')
    def test_broadcast_attempt_update(self, mock_emit_refetch):
        """
        Test attempt submission broadcast (no stored notification)
        """
        NotificationService.broadcast_attempt_update(
            event_id = 1,
            team_id = 5,
            challenge_id = 10,
            question_id = 15
        )

        expected_calls = [
            call(path = "/ng/events/1/challenges/10",
                 room = "team_5"),
            call(path = "/ng/events/1/leaderboard",
                 room = "event_1")
        ]
        mock_emit_refetch.assert_has_calls(expected_calls, any_order = False)

    @patch.object(NotificationService, '_emit_refetch')
    def test_broadcast_hint_redeemed(self, mock_emit_refetch):
        """
        Test hint redemption broadcast (WebSocket only)
        """
        NotificationService.broadcast_hint_redeemed(
            event_id = 2,
            team_id = 6,
            challenge_id = 11
        )

        mock_emit_refetch.assert_called_once_with(
            path = "/ng/events/2/challenges/11",
            room = "team_6"
        )

    @patch.object(NotificationService, '_emit_refetch')
    def test_broadcast_team_update(self, mock_emit_refetch):
        """
        Test team changes broadcast
        """
        NotificationService.broadcast_team_update(
            team_id = 7,
            update_type = "member_joined"
        )

        mock_emit_refetch.assert_called_once_with(
            path = "/ng/teams/7",
            room = "team_7"
        )


class TestEventAnnouncements:
    """
    Test event announcements (stored notifications + WebSocket)
    """
    @patch('ng.notifications.services.notification_service.db')
    @patch.object(NotificationService, '_emit_notification')
    @patch.object(NotificationService, '_emit_refetch')
    @patch('ng.notifications.services.notification_service.TeamMember')
    @patch.object(Announcement, 'create_announcement')
    @patch.object(Notification, 'create_notification')
    def test_send_event_announcement(
        self,
        mock_create_notification,
        mock_create_announcement,
        mock_team_member,
        mock_emit_refetch,
        mock_emit_notification,
        mock_db
    ):
        """
        Test sending event announcement to all participants
        """
        mock_announcement = Mock()
        mock_create_announcement.return_value = mock_announcement

        mock_member1 = Mock()
        mock_member1.user_id = 10
        mock_member2 = Mock()
        mock_member2.user_id = 11
        mock_team_member.query.filter_by.return_value.all.return_value = [
            mock_member1,
            mock_member2
        ]

        mock_notification1 = Mock()
        mock_notification2 = Mock()
        mock_create_notification.side_effect = [
            mock_notification1,
            mock_notification2
        ]

        result = NotificationService.send_event_announcement(
            event_id = 5,
            announcement_type = AnnouncementType.EVENT_START,
            title = "Event Beginning",
            message = "The event has started!",
            sender_id = 1
        )

        mock_create_announcement.assert_called_once_with(
            announcement_type = AnnouncementType.EVENT_START,
            title = "Event Beginning",
            message = "The event has started!",
            event_id = 5,
            sender_id = 1
        )

        mock_emit_notification.assert_has_calls(
            [call(mock_notification1),
             call(mock_notification2)]
        )

        mock_db.session.commit.assert_called_once()

        mock_emit_refetch.assert_called_once_with(
            path = "/ng/events/5/announcements",
            room = "event_5"
        )

        assert result == mock_announcement

    @patch('ng.notifications.services.notification_service.emit_event')
    @patch.object(Announcement, 'create_announcement')
    def test_send_system_announcement(
        self,
        mock_create_announcement,
        mock_emit_event
    ):
        """
        Test sending system-wide announcement
        """
        mock_announcement = Mock()
        mock_create_announcement.return_value = mock_announcement

        result = NotificationService.send_system_announcement(
            title = "System Maintenance",
            message = "Maintenance window tonight",
            sender_id = 1
        )

        mock_create_announcement.assert_called_once_with(
            announcement_type = AnnouncementType.GENERAL,
            title = "System Maintenance",
            message = "Maintenance window tonight",
            sender_id = 1
        )

        mock_emit_event.assert_called_once_with(
            event_name = "system_announcement",
            data = {
                "title": "System Maintenance",
                "message": "Maintenance window tonight"
            },
            room = None
        )

        assert result == mock_announcement


class TestTeamNotifications:
    """
    Test team-related notifications
    """
    @patch.object(NotificationService, '_emit_notification')
    @patch.object(Notification, 'create_notification')
    def test_notify_team_invitation(self, mock_create, mock_emit_notification):
        """
        Test team invitation notification
        """
        mock_notification = Mock()
        mock_create.return_value = mock_notification

        NotificationService.notify_team_invitation(
            team_id = 5,
            team_name = "Awesome Team",
            invited_user_id = 10,
            invited_by_id = 2
        )

        mock_create.assert_called_once_with(
            notification_type = NotificationType.TEAM_INVITATION,
            title = "Team Invitation",
            message = "You've been invited to join team 'Awesome Team'",
            recipient_id = 10,
            sender_id = 2,
            team_id = 5
        )

        mock_emit_notification.assert_called_once_with(mock_notification)


class TestChallengeNotifications:
    """
    Test challenge-related notifications
    """
    @patch('ng.notifications.services.notification_service.db')
    @patch.object(NotificationService, '_emit_notification')
    @patch.object(NotificationService, '_emit_refetch')
    @patch('ng.notifications.services.notification_service.TeamMember')
    @patch.object(Notification, 'create_notification')
    def test_notify_challenge_released(
        self,
        mock_create_notification,
        mock_team_member,
        mock_emit_refetch,
        mock_emit_notification,
        mock_db
    ):
        """
        Test new challenge release notification
        """
        mock_member1 = Mock()
        mock_member1.user_id = 20
        mock_member2 = Mock()
        mock_member2.user_id = 21
        mock_team_member.query.filter_by.return_value.all.return_value = [
            mock_member1,
            mock_member2
        ]

        mock_notification1 = Mock()
        mock_notification2 = Mock()
        mock_create_notification.side_effect = [
            mock_notification1,
            mock_notification2
        ]

        NotificationService.notify_challenge_released(
            event_id = 3,
            challenge_id = 15,
            challenge_name = "Crypto Master"
        )

        expected_calls = [
            call(
                notification_type = NotificationType.CHALLENGE_RELEASED,
                title = "New Challenge Available",
                message = "Challenge 'Crypto Master' is now available",
                recipient_id = 20,
                event_id = 3,
                challenge_id = 15,
                commit = False
            ),
            call(
                notification_type = NotificationType.CHALLENGE_RELEASED,
                title = "New Challenge Available",
                message = "Challenge 'Crypto Master' is now available",
                recipient_id = 21,
                event_id = 3,
                challenge_id = 15,
                commit = False
            )
        ]
        mock_create_notification.assert_has_calls(expected_calls)

        mock_emit_notification.assert_has_calls(
            [call(mock_notification1),
             call(mock_notification2)]
        )

        mock_db.session.commit.assert_called_once()

        mock_emit_refetch.assert_called_once_with(
            path = "/ng/events/3/challenges",
            room = "event_3"
        )


class TestServiceIntegration:
    """
    Integration tests for the service combining multiple features
    """
    @patch.object(NotificationService, '_emit_notification')
    @patch.object(NotificationService, '_emit_refetch')
    def test_mixed_notification_types(
        self,
        mock_emit_refetch,
        mock_emit_notification,
        db_session,
        user,
        admin
    ):
        """
        Test service handles different notification patterns correctly
        """
        # 1. Stored notification + refetch (ticket reply)
        with patch.object(Notification, 'create_notification') as mock_create:
            mock_notification = Mock()
            mock_create.return_value = mock_notification

            NotificationService.notify_ticket_reply(
                ticket_id = 1,
                author_id = admin.id,
                recipient_id = user.id,
                is_admin_reply = True
            )

            # Should create stored notification AND emit refetch
            mock_create.assert_called_once()
            mock_emit_notification.assert_called_with(mock_notification)
            mock_emit_refetch.assert_called_with(
                path = "/ng/support/tickets/1",
                room = "ticket_1"
            )

            mock_emit_notification.reset_mock()
            mock_emit_refetch.reset_mock()

        # 2. WebSocket only (attempt update)
        NotificationService.broadcast_attempt_update(
            event_id = 1,
            team_id = 5,
            challenge_id = 10,
            question_id = 15
        )

        # Should only emit refetch, no stored notification
        mock_emit_notification.assert_not_called()
        mock_emit_refetch.assert_called()

    @patch('ng.notifications.services.notification_service.emit_event')
    def test_websocket_error_handling(self, mock_emit_event):
        """
        Test service handles WebSocket errors gracefully
        """
        mock_emit_event.side_effect = Exception("WebSocket connection failed")

        try:
            NotificationService._emit_refetch("/test/path", "test_room")
            NotificationService.broadcast_attempt_update(1, 2, 3, 4)
        except Exception as e:
            pytest.fail(
                f"Service should handle WebSocket errors gracefully, but got: {e}"
            )

        assert mock_emit_event.call_count >= 2
