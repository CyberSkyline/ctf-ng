"""
Model tests for Notification
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timezone, UTC
from sqlalchemy.exc import SQLAlchemyError

from ..models.Notification import (
    Notification,
    NotificationType,
)
from ...core.exceptions import ValidationError


class TestNotificationRepr:
    def test_repr(self, notification_factory, user):
        """
        Test the string representation of the model
        """
        notification = notification_factory(
            type = NotificationType.TICKET_CREATE,
            recipient_id = user.id,
            title = "Test Notification"
        )
        expected = f"<Notification {notification.id}: type={NotificationType.TICKET_CREATE.value} recipient={user.id}>"
        assert repr(notification) == expected

    def test_repr_with_sender(self, notification_factory, user, admin):
        """
        Test string representation with sender
        """
        notification = notification_factory(
            type = NotificationType.TICKET_CREATE,
            recipient_id = user.id,
            sender_id = admin.id,
            title = "Test"
        )
        expected = f"<Notification {notification.id}: type={NotificationType.TICKET_CREATE.value} recipient={user.id}>"
        assert repr(notification) == expected


class TestNotification:
    def test_defaults(self):
        """
        Test the default values for a new instance
        """
        notification = Notification()
        assert notification.priority is None
        assert notification.sender_id is None
        assert notification.read_at is None
        assert notification.created_at is None
        assert notification.expires_at is None
        assert notification.ticket_id is None
        assert notification.team_id is None
        assert notification.event_id is None
        assert notification.challenge_id is None

    def test_create_notification_minimal(self, db_session, user):
        """
        Test creating a notification with minimal required fields
        """
        notification = Notification.create_notification(
            notification_type = NotificationType.TICKET_CREATE,
            title = "Test Title",
            message = "Test message",
            recipient_id = user.id
        )

        refreshed_notification = Notification.find_by_id(notification.id)
        assert refreshed_notification is not None
        assert refreshed_notification.type == NotificationType.TICKET_CREATE
        assert refreshed_notification.title == "Test Title"
        assert refreshed_notification.message == "Test message"
        assert refreshed_notification.priority is None
        assert refreshed_notification.recipient_id == user.id
        assert refreshed_notification.sender_id is None
        assert refreshed_notification.read_at is None
        assert refreshed_notification.created_at is not None
        assert refreshed_notification.expires_at is None

    def test_create_notification_full_fields(
        self,
        db_session,
        user,
        admin,
        ticket,
        team_with_member,
        event,
        challenge
    ):
        """
        Test creating a notification with all fields populated
        """
        notification = Notification.create_notification(
            notification_type = NotificationType.TICKET_MESSAGE,
            title = "Ticket Updated",
            message = "Your ticket has been updated",
            recipient_id = user.id,
            sender_id = admin.id,
            priority = "high",
            ticket_id = ticket.id,
            team_id = team_with_member.id,
            event_id = event.id,
            challenge_id = challenge.id
        )

        refreshed_notification = Notification.find_by_id(notification.id)
        assert refreshed_notification is not None
        assert refreshed_notification.type == NotificationType.TICKET_MESSAGE
        assert refreshed_notification.title == "Ticket Updated"
        assert refreshed_notification.message == "Your ticket has been updated"
        assert refreshed_notification.recipient_id == user.id
        assert refreshed_notification.sender_id == admin.id
        assert refreshed_notification.priority == "high"
        assert refreshed_notification.ticket_id == ticket.id
        assert refreshed_notification.team_id == team_with_member.id
        assert refreshed_notification.event_id == event.id
        assert refreshed_notification.challenge_id == challenge.id

    def test_create_notification_respects_commit_flag(self, db_session, user):
        """
        Test that create respects the commit flag
        """
        with patch.object(db_session, "commit") as mock_commit:
            notification = Notification.create_notification(
                notification_type = NotificationType.TICKET_CREATE,
                title = "No Commit",
                message = "This should not be committed",
                recipient_id = user.id,
                commit = False
            )
            mock_commit.assert_not_called()
            assert notification.title == "No Commit"

        with patch.object(db_session, "commit") as mock_commit:
            Notification.create_notification(
                notification_type = NotificationType.TICKET_CREATE,
                title = "With Commit",
                message = "This should be committed",
                recipient_id = user.id,
                commit = True
            )
            mock_commit.assert_called_once()

    def test_create_notification_invalid_type_fails(self, db_session, user):
        """
        Test that creating notification with invalid type fails validation
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.create_notification(
                notification_type = "invalid_type",
                title = "Test",
                message = "Test message",
                recipient_id = user.id
            )
        assert "type" in exc_info.value.errors

    def test_create_notification_missing_title_fails(self, db_session, user):
        """
        Test that creating notification without title fails validation
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.create_notification(
                notification_type = NotificationType.TICKET_CREATE,
                title = "",
                message = "Test message",
                recipient_id = user.id
            )
        assert "title" in exc_info.value.errors

    def test_create_notification_missing_message_fails(self, db_session, user):
        """
        Test that creating notification without message fails validation
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.create_notification(
                notification_type = NotificationType.TICKET_CREATE,
                title = "Test Title",
                message = "",
                recipient_id = user.id
            )
        assert "message" in exc_info.value.errors

    def test_create_notification_invalid_user_id_fails(self, db_session):
        """
        Test that creating notification with invalid user ID fails
        """
        with pytest.raises(ValidationError):
            Notification.create_notification(
                notification_type = NotificationType.TICKET_CREATE,
                title = "Test",
                message = "Test message",
                recipient_id = 999999
            )

    def test_create_notification_invalid_ticket_id_fails(
        self,
        db_session,
        user
    ):
        """
        Test that creating notification with invalid ticket ID fails
        """
        with pytest.raises(ValidationError):
            Notification.create_notification(
                notification_type = NotificationType.TICKET_MESSAGE,
                title = "Test",
                message = "Test message",
                recipient_id = user.id,
                ticket_id = 999999
            )

    def test_mark_as_read(self, db_session, notification_factory, user):
        """
        Test marking a notification as read
        """
        notification = notification_factory(
            recipient_id = user.id,
            read_at = None
        )
        notification_id = notification.id
        assert notification.is_read is False
        assert notification.read_at is None

        notification.mark_as_read()

        refreshed_notification = Notification.find_by_id(notification_id)
        assert refreshed_notification is not None
        assert refreshed_notification.is_read is True
        assert refreshed_notification.read_at is not None

    def test_mark_as_read_respects_commit_flag(
        self,
        db_session,
        notification_factory,
        user
    ):
        """
        Test that mark_as_read respects the commit flag
        """
        notification = notification_factory(
            recipient_id = user.id,
            read_at = None
        )

        with patch.object(db_session, "commit") as mock_commit:
            notification.mark_as_read(commit = False)
            mock_commit.assert_not_called()

        notification.read_at = None
        with patch.object(db_session, "commit") as mock_commit:
            notification.mark_as_read(commit = True)
            mock_commit.assert_called_once()

    def test_find_by_recipient_id(
        self,
        db_session,
        notification_factory,
        user,
        admin
    ):
        """
        Test filtering notifications by recipient ID
        """
        user_notification = notification_factory(
            recipient_id = user.id,
            title = "User notification"
        )
        notification_factory(
            recipient_id = admin.id,
            title = "Admin notification"
        )

        user_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id
        )

        assert len(user_notifications) == 1
        assert user_notifications[0].id == user_notification.id
        assert user_notifications[0].title == "User notification"

    def test_find_by_read_status(self, db_session, notification_factory, user):
        """
        Test filtering notifications by read status
        """
        read_notification = notification_factory(
            recipient_id = user.id,
            read_at = datetime(6969,
                               1,
                               1,
                               tzinfo = UTC),
            title = "Read"
        )
        unread_notification = notification_factory(
            recipient_id = user.id,
            read_at = None,
            title = "Unread"
        )

        unread_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id,
            is_read = False
        )

        assert len(unread_notifications) == 1
        assert unread_notifications[0].id == unread_notification.id

        read_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id,
            is_read = True
        )

        assert len(read_notifications) == 1
        assert read_notifications[0].id == read_notification.id

    def test_find_by_notification_type(
        self,
        db_session,
        notification_factory,
        user
    ):
        """
        Test filtering notifications by type
        """
        ticket_notification = notification_factory(
            recipient_id = user.id,
            type = NotificationType.TICKET_CREATE,
            title = "Ticket"
        )
        notification_factory(
            recipient_id = user.id,
            type = NotificationType.ATTEMPT_SUBMISSION,
            title = "Attempt"
        )

        ticket_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id,
            notification_type = NotificationType.TICKET_CREATE
        )

        assert len(ticket_notifications) == 1
        assert ticket_notifications[0].id == ticket_notification.id

    def test_find_by_type_with_expiration(
        self,
        db_session,
        notification_factory,
        user
    ):
        """
        Test filtering by type and expiration
        """
        active_notification = notification_factory(
            recipient_id = user.id,
            type = NotificationType.TICKET_CREATE,
            expires_at = None,
            title = "Active"
        )
        notification_factory(
            recipient_id = user.id,
            type = NotificationType.TICKET_CREATE,
            expires_at = datetime(6969,
                                  1,
                                  1),
            title = "Expired"
        )

        active_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id,
            notification_type = NotificationType.TICKET_CREATE
        )

        assert len(active_notifications) == 1
        assert active_notifications[0].id == active_notification.id

        all_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id,
            notification_type = NotificationType.TICKET_CREATE,
            expired = True
        )

        assert len(all_notifications) == 2

    def test_find_with_limit(self, db_session, notification_factory, user):
        """
        Test filtering with limit parameter
        """
        notifications = []
        for i in range(5):
            notification = notification_factory(
                recipient_id = user.id,
                title = f"Notification {i}"
            )
            notifications.append(notification)

        limited_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id,
            limit = 3
        )

        assert len(limited_notifications) == 3

    def test_find_ordered_by_created_at_desc(
        self,
        db_session,
        notification_factory,
        user
    ):
        """
        Test that notifications are ordered by created_at descending
        """
        notification_factory(
            recipient_id = user.id,
            title = "Old",
            created_at = datetime(6969,
                                  8,
                                  15,
                                  10,
                                  0,
                                  0,
                                  tzinfo = UTC)
        )
        notification_factory(
            recipient_id = user.id,
            title = "New",
            created_at = datetime(6969,
                                  8,
                                  17,
                                  12,
                                  0,
                                  0,
                                  tzinfo = UTC)
        )
        notification_factory(
            recipient_id = user.id,
            title = "Middle",
            created_at = datetime(6969,
                                  8,
                                  16,
                                  11,
                                  0,
                                  0,
                                  tzinfo = UTC)
        )

        notifications = Notification.find_filtered_notifications(
            recipient_id = user.id
        )

        assert len(notifications) == 3
        assert notifications[0].title == "New"
        assert notifications[1].title == "Middle"
        assert notifications[2].title == "Old"

    def test_find_combined_filters(
        self,
        db_session,
        notification_factory,
        user,
        admin
    ):
        """
        Test combining multiple filters
        """
        target_notification = notification_factory(
            recipient_id = user.id,
            read_at = None,
            type = NotificationType.TICKET_CREATE,
            title = "Target"
        )

        notification_factory(
            recipient_id = admin.id,
            read_at = None,
            type = NotificationType.TICKET_CREATE,
            title = "Wrong recipient"
        )

        notification_factory(
            recipient_id = user.id,
            read_at = datetime(6969,
                               1,
                               1,
                               tzinfo = UTC),
            type = NotificationType.TICKET_CREATE,
            title = "Wrong read status"
        )

        notification_factory(
            recipient_id = user.id,
            read_at = None,
            type = NotificationType.ATTEMPT_SUBMISSION,
            title = "Wrong type"
        )

        filtered_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id,
            is_read = False,
            notification_type = NotificationType.TICKET_CREATE
        )

        assert len(filtered_notifications) == 1
        assert filtered_notifications[0].id == target_notification.id

    def test_get_unread_count(
        self,
        db_session,
        notification_factory,
        user,
        admin
    ):
        """
        Test getting unread notification count
        """
        notification_factory(recipient_id = user.id, read_at = None)
        notification_factory(recipient_id = user.id, read_at = None)

        notification_factory(
            recipient_id = user.id,
            read_at = datetime(6969,
                               1,
                               1,
                               tzinfo = UTC)
        )
        notification_factory(recipient_id = admin.id, read_at = None)
        notification_factory(
            recipient_id = user.id,
            read_at = None,
            expires_at = datetime(6969,
                                  1,
                                  1,
                                  tzinfo = UTC)
        )

        count = Notification.get_unread_count(user.id)
        assert count == 2

    def test_mark_all_as_read(
        self,
        db_session,
        notification_factory,
        user,
        admin
    ):
        """
        Test marking all notifications as read for a user
        """
        notification_factory(recipient_id = user.id, read_at = None)
        notification_factory(recipient_id = user.id, read_at = None)
        notification_factory(recipient_id = admin.id, read_at = None)

        count = Notification.mark_all_as_read(user.id)
        assert count == 2

        user_unread_count = Notification.get_unread_count(user.id)
        assert user_unread_count == 0

        admin_unread_count = Notification.get_unread_count(admin.id)
        assert admin_unread_count == 1

    def test_delete_expired(self, db_session, notification_factory, user):
        """
        Test deleting expired notifications
        """
        active_notification = notification_factory(
            recipient_id = user.id,
            expires_at = None,
            title = "Active"
        )
        notification_factory(
            recipient_id = user.id,
            expires_at = datetime(6969,
                                  1,
                                  1,
                                  tzinfo = UTC),
            title = "Expired"
        )

        count = Notification.delete_expired()
        assert count == 1

        remaining_notifications = Notification.find_filtered_notifications(
            recipient_id = user.id,
            expired = True
        )
        assert len(remaining_notifications) == 1
        assert remaining_notifications[0].id == active_notification.id

    def test_serialize_basic(self, notification_factory, user, admin):
        """
        Test basic notification serialization
        """
        notification = notification_factory(
            type = NotificationType.TICKET_CREATE,
            priority = "normal",
            title = "Test Notification",
            message = "Test message",
            recipient_id = user.id,
            sender_id = admin.id,
            read_at = None
        )

        data = notification.serialize()

        assert data["id"] == notification.id
        assert data["type"] == NotificationType.TICKET_CREATE.value
        assert data["priority"] == "normal"
        assert data["title"] == "Test Notification"
        assert data["message"] == "Test message"
        assert data["recipient_id"] == user.id
        assert data["sender_id"] == admin.id
        assert data["read_at"] is None
        assert isinstance(data["created_at"], str)
        assert data["created_at"].endswith("Z")
        assert data["expires_at"] is None

    def test_serialize_with_reference_fields(
        self,
        notification_factory,
        user,
        ticket,
        team_with_member,
        event,
        challenge
    ):
        """
        Test serialization with reference fields
        """
        notification = notification_factory(
            recipient_id = user.id,
            ticket_id = ticket.id,
            team_id = team_with_member.id,
            event_id = event.id,
            challenge_id = challenge.id
        )

        data = notification.serialize()

        assert "ticket_id" in data
        assert data["ticket_id"] == ticket.id
        assert "team_id" in data
        assert data["team_id"] == team_with_member.id
        assert "event_id" in data
        assert data["event_id"] == event.id
        assert "challenge_id" in data
        assert data["challenge_id"] == challenge.id

    def test_serialize_without_reference_fields(
        self,
        notification_factory,
        user
    ):
        """
        Test serialization without optional reference fields
        """
        notification = notification_factory(
            recipient_id = user.id,
            ticket_id = None,
            team_id = None,
            event_id = None,
            challenge_id = None
        )

        data = notification.serialize()

        assert "ticket_id" not in data
        assert "team_id" not in data
        assert "event_id" not in data
        assert "challenge_id" not in data

    def test_serialize_with_read_timestamp(self, notification_factory, user):
        """
        Test serialization with read timestamp
        """
        read_time = datetime(6969, 1, 1, 12, 0, 0, tzinfo = UTC)
        notification = notification_factory(
            type = NotificationType.TICKET_CREATE,
            recipient_id = user.id,
            title = "Read Notification",
            message = "This has been read",
            read_at = read_time
        )

        data = notification.serialize()

        assert data["read_at"] == "2023-01-01T12:00:00Z"
        assert data["type"] == NotificationType.TICKET_CREATE.value
        assert data["title"] == "Read Notification"

    def test_validate_valid_data(self, db_session, user, admin):
        """
        Test validation with valid data
        """
        data = Notification.validate(
            {
                "type": NotificationType.TICKET_CREATE,
                "title": "Test Title",
                "message": "Test message",
                "priority": "high",
                "recipient_id": user.id,
                "sender_id": admin.id,
            }
        )

        assert data["type"] == NotificationType.TICKET_CREATE
        assert data["title"] == "Test Title"
        assert data["message"] == "Test message"
        assert data["priority"] == "high"
        assert data["recipient_id"] == user.id
        assert data["sender_id"] == admin.id

    def test_validate_missing_type_fails(self, db_session, user):
        """
        Test validation fails with missing type
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.validate(
                {
                    "title": "Test Title",
                    "message": "Test message",
                    "recipient_id": user.id
                }
            )
        assert "type" in exc_info.value.errors

    def test_validate_missing_title_fails(self, db_session, user):
        """
        Test validation fails with missing title
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.validate(
                {
                    "type": NotificationType.TICKET_CREATE,
                    "message": "Test message",
                    "recipient_id": user.id
                }
            )
        assert "title" in exc_info.value.errors

    def test_validate_missing_message_fails(self, db_session, user):
        """
        Test validation fails with missing message
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.validate(
                {
                    "type": NotificationType.TICKET_CREATE,
                    "title": "Test Title",
                    "recipient_id": user.id
                }
            )
        assert "message" in exc_info.value.errors

    def test_validate_invalid_priority(self, db_session, user):
        """
        Test validation fails with invalid priority
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.validate(
                {
                    "type": NotificationType.TICKET_CREATE,
                    "title": "Test Title",
                    "message": "Test message",
                    "priority": "x" * 100,
                    "recipient_id": user.id
                }
            )
        assert "priority" in exc_info.value.errors

    def test_validate_empty_title_fails(self, db_session, user):
        """
        Test that empty/whitespace titles are rejected
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.validate(
                {
                    "type": NotificationType.TICKET_CREATE,
                    "title": "   ",
                    "message": "Test message",
                    "recipient_id": user.id
                }
            )
        assert "title" in exc_info.value.errors

    def test_validate_empty_message_fails(self, db_session, user):
        """
        Test that empty/whitespace messages are rejected
        """
        with pytest.raises(ValidationError) as exc_info:
            Notification.validate(
                {
                    "type": NotificationType.TICKET_CREATE,
                    "title": "Test Title",
                    "message": "   ",
                    "recipient_id": user.id
                }
            )
        assert "message" in exc_info.value.errors

    def test_notification_type_enum_values(self):
        """
        Test NotificationType enum values
        """
        assert NotificationType.TICKET_CREATE.value == "ticket_create"
        assert NotificationType.TICKET_MESSAGE.value == "ticket_message"
        assert NotificationType.TICKET_STATUS_CHANGE.value == "ticket_status_change"
        assert NotificationType.TICKET_ASSIGNED.value == "ticket_assigned"
        assert NotificationType.ATTEMPT_SUBMISSION.value == "attempt_submission"
        assert NotificationType.TEAM_INVITATION.value == "team_invitation"
        assert NotificationType.CHALLENGE_RELEASED.value == "challenge_released"

    def test_is_read_property(self, notification_factory, user):
        """
        Test the is_read property
        """
        unread_notification = notification_factory(
            recipient_id = user.id,
            read_at = None
        )
        read_notification = notification_factory(
            recipient_id = user.id,
            read_at = datetime(6969,
                               1,
                               1)
        )

        assert unread_notification.is_read is False
        assert read_notification.is_read is True

    def test_recipient_relationship(self, notification_factory, user):
        """
        Test the recipient relationship
        """
        notification = notification_factory(recipient_id = user.id)

        assert notification.recipient is not None
        assert notification.recipient.id == user.id

    def test_sender_relationship(self, notification_factory, admin):
        """
        Test the sender relationship
        """
        notification = notification_factory(sender_id = admin.id)

        assert notification.sender is not None
        assert notification.sender.id == admin.id

    def test_notification_with_expiration(self, notification_factory, user):
        """
        Test notification with expiration date
        """
        expiry_date = datetime(6969, 12, 31, 23, 59, 59, tzinfo = UTC)
        notification = notification_factory(
            recipient_id = user.id,
            expires_at = expiry_date
        )

        assert notification.expires_at == expiry_date.replace(tzinfo = None)
