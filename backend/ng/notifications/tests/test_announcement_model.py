"""
Model tests for Announcement
"""

import pytest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone, UTC

from ..models.Announcement import (
        Announcement,
        AnnouncementType,
        )
from ...core.exceptions import ValidationError


class TestAnnouncementRepr:
    def test_repr(self, announcement_factory):
        """
        Test the string representation of the model
        """
        announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                title = "Test Announcement"
                )
        expected = f"<Announcement {announcement.id}: type={AnnouncementType.GENERAL.value}>"
        assert repr(announcement) == expected

    def test_repr_event_specific(self, announcement_factory, event):
        """
        Test string representation for event-specific announcement
        """
        announcement = announcement_factory(
                type = AnnouncementType.EVENT_UPDATE,
                event_id = event.id,
                title = "Event Update"
                )
        expected = f"<Announcement {announcement.id}: type={AnnouncementType.EVENT_UPDATE.value}>"
        assert repr(announcement) == expected


class TestAnnouncement:
    def test_defaults(self):
        """
        Test the default values for a new instance
        """
        announcement = Announcement()
        assert announcement.sender_id is None
        assert announcement.created_at is None
        assert announcement.expires_at is None
        assert announcement.event_id is None

    def test_create_announcement_minimal(self, db_session):
        """
        Test creating an announcement with minimal required fields
        """
        announcement = Announcement.create_announcement(
                announcement_type = AnnouncementType.GENERAL,
                title = "Test Title",
                message = "Test message"
                )

        refreshed_announcement = Announcement.find_by_id(announcement.id)
        assert refreshed_announcement is not None
        assert refreshed_announcement.type == AnnouncementType.GENERAL
        assert refreshed_announcement.title == "Test Title"
        assert refreshed_announcement.message == "Test message"
        assert refreshed_announcement.sender_id is None
        assert refreshed_announcement.created_at is not None
        assert refreshed_announcement.expires_at is None
        assert refreshed_announcement.event_id is None

    def test_create_announcement_full_fields(self, db_session, admin, event):
        """
        Test creating an announcement with all fields populated
        """
        expires_at = "2025-12-31T23:59:59Z"

        announcement = Announcement.create_announcement(
                announcement_type = AnnouncementType.EVENT_UPDATE,
                title = "Event Starting Soon",
                message = "The event will begin in 30 minutes",
                sender_id = admin.id,
                event_id = event.id,
                expires_at = expires_at
                )

        refreshed_announcement = Announcement.find_by_id(announcement.id)
        assert refreshed_announcement is not None
        assert refreshed_announcement.type == AnnouncementType.EVENT_UPDATE
        assert refreshed_announcement.title == "Event Starting Soon"
        assert refreshed_announcement.message == "The event will begin in 30 minutes"
        assert refreshed_announcement.sender_id == admin.id
        assert refreshed_announcement.event_id == event.id
        assert refreshed_announcement.expires_at == datetime(
                2025,
                12,
                31,
                23,
                59,
                59
                )

    def test_create_announcement_respects_commit_flag(self, db_session):
        """
        Test that create respects the commit flag
        """
        with patch.object(db_session, "commit") as mock_commit:
            announcement = Announcement.create_announcement(
                    announcement_type = AnnouncementType.GENERAL,
                    title = "No Commit",
                    message = "This should not be committed",
                    commit = False
                    )
            mock_commit.assert_not_called()
            assert announcement.title == "No Commit"

        with patch.object(db_session, "commit") as mock_commit:
            Announcement.create_announcement(
                    announcement_type = AnnouncementType.GENERAL,
                    title = "With Commit",
                    message = "This should be committed",
                    commit = True
                    )
            mock_commit.assert_called_once()

    def test_create_announcement_invalid_type_fails(self, db_session):
        """
        Test that creating announcement with invalid type fails validation
        """
        with pytest.raises(ValidationError) as exc_info:
            Announcement.create_announcement(
                    announcement_type = "invalid_type",
                    title = "Test",
                    message = "Test message"
                    )
        assert "type" in exc_info.value.errors

    def test_create_announcement_missing_title_fails(self, db_session):
        """
        Test that creating announcement without title fails validation
        """
        with pytest.raises(ValidationError) as exc_info:
            Announcement.create_announcement(
                    announcement_type = AnnouncementType.GENERAL,
                    title = "",
                    message = "Test message"
                    )
        assert "title" in exc_info.value.errors

    def test_create_announcement_missing_message_fails(self, db_session):
        """
        Test that creating announcement without message fails validation
        """
        with pytest.raises(ValidationError) as exc_info:
            Announcement.create_announcement(
                    announcement_type = AnnouncementType.GENERAL,
                    title = "Test Title",
                    message = ""
                    )
        assert "message" in exc_info.value.errors

    def test_create_announcement_invalid_user_id_fails(self, db_session):
        """
        Test that creating announcement with invalid user ID fails
        """
        with pytest.raises(ValidationError):
            Announcement.create_announcement(
                    announcement_type = AnnouncementType.GENERAL,
                    title = "Test",
                    message = "Test message",
                    sender_id = 999999
                    )

    def test_create_announcement_invalid_event_id_fails(self, db_session):
        """
        Test that creating announcement with invalid event ID fails
        """
        with pytest.raises(ValidationError):
            Announcement.create_announcement(
                    announcement_type = AnnouncementType.EVENT_UPDATE,
                    title = "Test",
                    message = "Test message",
                    event_id = 999999
                    )

    def test_is_active_property_no_expiration(self, announcement_factory):
        """
        Test is_active property for announcement without expiration
        """
        announcement = announcement_factory(expires_at = None)
        assert announcement.is_active is True

    def test_is_active_property_future_expiration(self, announcement_factory):
        """
        Test is_active property for announcement with future expiration
        """
        future_date = datetime(6969, 12, 31, 23, 59, 59, tzinfo = UTC)
        announcement = announcement_factory(expires_at = future_date)
        assert announcement.is_active is True

    def test_is_active_property_past_expiration(self, announcement_factory):
        """
        Test is_active property for expired announcement
        """
        past_date = datetime(1969, 1, 1, 0, 0, 0, tzinfo = UTC)
        announcement = announcement_factory(expires_at = past_date)
        assert announcement.is_active is False

    def test_get_active_announcements_global(
            self,
            db_session,
            announcement_factory
            ):
        """
        Test getting active global announcements
        """
        active_announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                event_id = None,
                expires_at = None,
                title = "Active Global"
                )
        announcement_factory(
                type = AnnouncementType.GENERAL,
                event_id = None,
                expires_at = datetime(1969,
                                      1,
                                      1,
                                      tzinfo = UTC),
                title = "Expired Global"
                )

        active_announcements = Announcement.get_active_announcements()

        assert len(active_announcements) == 1
        assert active_announcements[0].id == active_announcement.id
        assert active_announcements[0].title == "Active Global"

    def test_get_active_announcements_event_specific(
            self,
            db_session,
            announcement_factory,
            event
            ):
        """
        Test getting active event-specific announcements
        """
        event_announcement = announcement_factory(
                type = AnnouncementType.EVENT_UPDATE,
                event_id = event.id,
                expires_at = None,
                title = "Event Update"
                )
        announcement_factory(
                type = AnnouncementType.GENERAL,
                event_id = None,
                title = "Global"
                )

        event_announcements = Announcement.get_active_announcements(
                event_id = event.id
                )

        assert len(event_announcements) == 1
        assert event_announcements[0].id == event_announcement.id
        assert event_announcements[0].title == "Event Update"

    def test_get_active_announcements_returns_all(
            self,
            db_session,
            announcement_factory
            ):
        """
        Test getting all active announcements
        """
        announcements = []
        for i in range(5):
            announcement = announcement_factory(
                    type = AnnouncementType.GENERAL,
                    event_id = None,
                    title = f"Announcement {i}"
                    )
            announcements.append(announcement)

        all_announcements = Announcement.get_active_announcements()

        assert len(all_announcements) == 5

    def test_get_active_announcements_ordered_by_created_desc(
            self,
            db_session,
            announcement_factory
            ):
        """
        Test that announcements are ordered by created_at descending
        """
        old_announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                title = "Old",
                created_at = datetime(6969,
                                      1,
                                      1,
                                      10,
                                      0,
                                      0,
                                      tzinfo = UTC)
                )
        new_announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                title = "New",
                created_at = datetime(6969,
                                      1,
                                      2,
                                      10,
                                      0,
                                      0,
                                      tzinfo = UTC)
                )

        announcements = Announcement.get_active_announcements()

        assert len(announcements) == 2
        assert announcements[0].id == new_announcement.id
        assert announcements[1].id == old_announcement.id

    def test_delete_expired(self, db_session, announcement_factory):
        """
        Test deleting expired announcements
        """
        active_announcement = announcement_factory(
                expires_at = None,
                title = "Active"
                )
        announcement_factory(
                expires_at = datetime(1969,
                                      1,
                                      1,
                                      tzinfo = UTC),
                title = "Expired"
                )

        count = Announcement.delete_expired()
        assert count == 1

        remaining_announcements = Announcement.get_active_announcements()
        assert len(remaining_announcements) == 1
        assert remaining_announcements[0].id == active_announcement.id

    def test_serialize_basic(self, announcement_factory, admin):
        """
        Test basic announcement serialization
        """
        announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                title = "Test Announcement",
                message = "Test message",
                sender_id = admin.id
                )

        data = announcement.serialize()

        assert data["id"] == announcement.id
        assert data["type"] == AnnouncementType.GENERAL.value
        assert data["title"] == "Test Announcement"
        assert data["message"] == "Test message"
        assert data["sender_id"] == admin.id
        assert isinstance(data["created_at"], str)
        assert data["created_at"].endswith("Z")
        assert data["expires_at"] is None

    def test_serialize_with_event_reference(self, announcement_factory, event):
        """
        Test serialization with event reference
        """
        announcement = announcement_factory(
                type = AnnouncementType.EVENT_UPDATE,
                event_id = event.id,
                title = "Event Update"
                )

        data = announcement.serialize()

        assert "event_id" in data
        assert data["event_id"] == event.id

    def test_serialize_without_optional_fields(self, announcement_factory):
        """
        Test serialization without optional fields
        """
        announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                sender_id = None,
                event_id = None
                )

        data = announcement.serialize()

        assert "event_id" not in data
        assert data["sender_id"] is None

    def test_serialize_with_expiration(self, announcement_factory):
        """
        Test serialization with expiration date
        """
        expiry_date = datetime(1969, 12, 31, 23, 59, 59, tzinfo = UTC)
        announcement = announcement_factory(
                type = AnnouncementType.GENERAL,
                expires_at = expiry_date
                )

        data = announcement.serialize()

        assert data["expires_at"] == "1969-12-31T23:59:59Z"

    def test_validate_valid_data(self, db_session, admin, event):
        """
        Test validation with valid data
        """
        data = Announcement.validate(
                {
                        "type": AnnouncementType.EVENT_UPDATE,
                        "title": "Test Title",
                        "message": "Test message",
                        "sender_id": admin.id,
                        "event_id": event.id,
                        }
                )

        assert data["type"] == AnnouncementType.EVENT_UPDATE
        assert data["title"] == "Test Title"
        assert data["message"] == "Test message"
        assert data["sender_id"] == admin.id
        assert data["event_id"] == event.id

    def test_validate_missing_type_fails(self, db_session):
        """
        Test validation fails with missing type
        """
        with pytest.raises(ValidationError) as exc_info:
            Announcement.validate(
                    {
                            "title": "Test Title",
                            "message": "Test message"
                            }
                    )
        assert "type" in exc_info.value.errors

    def test_validate_missing_title_fails(self, db_session):
        """
        Test validation fails with missing title
        """
        with pytest.raises(ValidationError) as exc_info:
            Announcement.validate(
                    {
                            "type": AnnouncementType.GENERAL,
                            "message": "Test message"
                            }
                    )
        assert "title" in exc_info.value.errors

    def test_validate_missing_message_fails(self, db_session):
        """
        Test validation fails with missing message
        """
        with pytest.raises(ValidationError) as exc_info:
            Announcement.validate(
                    {
                            "type": AnnouncementType.GENERAL,
                            "title": "Test Title"
                            }
                    )
        assert "message" in exc_info.value.errors

    def test_validate_empty_title_fails(self, db_session):
        """
        Test that empty/whitespace titles are rejected
        """
        with pytest.raises(ValidationError) as exc_info:
            Announcement.validate(
                    {
                            "type": AnnouncementType.GENERAL,
                            "title": "   ",
                            "message": "Test message"
                            }
                    )
        assert "title" in exc_info.value.errors

    def test_validate_empty_message_fails(self, db_session):
        """
        Test that empty/whitespace messages are rejected
        """
        with pytest.raises(ValidationError) as exc_info:
            Announcement.validate(
                    {
                            "type": AnnouncementType.GENERAL,
                            "title": "Test Title",
                            "message": "   "
                            }
                    )
        assert "message" in exc_info.value.errors

    def test_announcement_type_enum_values(self):
        """
        Test AnnouncementType enum values
        """
        assert AnnouncementType.GENERAL.value == "general"
        assert AnnouncementType.EVENT_UPDATE.value == "event_update"
        assert AnnouncementType.EVENT_START.value == "event_start"
        assert AnnouncementType.EVENT_END.value == "event_end"
        assert AnnouncementType.LEADERBOARD_UPDATE.value == "leaderboard_update"

    def test_sender_relationship(self, announcement_factory, admin):
        """
        Test the sender relationship
        """
        announcement = announcement_factory(sender_id = admin.id)

        assert announcement.sender is not None
        assert announcement.sender.id == admin.id

    def test_event_relationship(self, announcement_factory, event):
        """
        Test the event relationship
        """
        announcement = announcement_factory(event_id = event.id)

        assert announcement.event is not None
        assert announcement.event.id == event.id

    def test_announcement_without_sender(self, announcement_factory):
        """
        Test announcement with no sender
        """
        announcement = announcement_factory(sender_id = None)

        assert announcement.sender is None

    def test_global_announcement_no_event(self, announcement_factory):
        """
        Test global announcement has no event
        """
        announcement = announcement_factory(event_id = None)

        assert announcement.event is None
