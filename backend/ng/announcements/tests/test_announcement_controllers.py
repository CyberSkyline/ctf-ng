"""
Tests for announcement controllers
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import patch, Mock

from ...core.exceptions import ValidationError
from ..controllers import (
    send_announcement,
    send_event_announcement,
    get_all_announcements,
    get_active_announcements,
)
from ..models import (
    Announcement,
    AnnouncementType,
)
from ..services import AnnouncementService


class TestSendAnnouncement:
    """
    Test the send_announcement controller
    """
    @patch.object(AnnouncementService, 'send_system_announcement')
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
            sender_id = admin.id
        )
        assert result == mock_announcement

    @patch.object(AnnouncementService, 'send_system_announcement')
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
            sender_id = None
        )
        assert result is None


class TestSendEventAnnouncement:
    """
    Test the send_event_announcement controller
    """
    @patch.object(AnnouncementService, 'send_event_announcement')
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

    def test_send_event_announcement_invalid_type(self, db_session, admin, event):
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

    @patch.object(AnnouncementService, 'send_event_announcement')
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

        mock_get_active.assert_called_once_with(event_id = event.id)
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
    Integration tests for announcement controllers working together
    """
    @patch.object(AnnouncementService, 'send_system_announcement')
    @patch.object(AnnouncementService, 'send_event_announcement')
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
            sender_id = admin.id
        )
        mock_send_event.assert_called_once_with(
            event_id = event.id,
            announcement_type = AnnouncementType.EVENT_START,
            title = "Event Starting",
            message = "Get ready!",
            sender_id = admin.id
        )
