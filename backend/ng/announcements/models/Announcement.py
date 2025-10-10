"""
Defines the Announcement model for system-wide banner messages
"""

from __future__ import annotations

from enum import Enum
from typing import (
    Any,
    TypedDict,
    NotRequired,
)

from CTFd.models import db

from ... import config
from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator
from ...notifications.models import Notification


class AnnouncementType(str, Enum):
    GENERAL = "general"
    EVENT_UPDATE = "event_update"
    EVENT_START = "event_start"
    EVENT_END = "event_end"
    LEADERBOARD_UPDATE = "leaderboard_update"


class SerializedAnnouncement(TypedDict):
    id: int
    type: str
    title: str
    message: str
    sender_id: int | None
    created_at: str
    expires_at: str | None
    # Optional reference fields
    event_id: NotRequired[int | None]
    # Name enrichment fields
    sender_name: NotRequired[str | None]
    event_name: NotRequired[str | None]


class Announcement(db.Model):
    __tablename__ = "ng_announcements"

    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.Enum(AnnouncementType), nullable = False)
    title = db.Column(
        db.String(config.NOTIFICATIONS_TITLE_MAX_LENGTH),
        nullable = False
    )
    message = db.Column(
        db.String(config.NOTIFICATIONS_MESSAGE_MAX_LENGTH),
        nullable = False
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable = True
    )
    created_at = db.Column(db.DateTime, default = utc_now, nullable = False)
    expires_at = db.Column(db.DateTime, nullable = True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_events.id"),
        nullable = True,
        index = True
    )

    __table_args__ = (
        db.Index("ix_ng_announcements_expires",
                 "expires_at"),
        db.Index("ix_ng_announcements_created",
                 "created_at"),
    )

    sender = db.relationship(
        "Users",
        foreign_keys = [sender_id],
        backref = "announcements_sent"
    )
    event = db.relationship("Event", backref = "announcements")

    def __repr__(self):
        return f"<Announcement {self.id}: type={self.type.value}>"

    @property
    def is_active(self) -> bool:
        """
        Check if announcement is currently active
        """
        if self.expires_at and self.expires_at <= utc_now().replace(tzinfo=None):
            return False
        return True

    def serialize(
        self,
        include_admin_fields: bool = False
    ) -> SerializedAnnouncement:
        """
        Serialize announcement for API response

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized announcement data
        """
        data = {
            "id":
            self.id,
            "type":
            self.type.value,
            "title":
            self.title,
            "message":
            self.message,
            "sender_id":
            self.sender_id,
            "created_at":
            self.created_at.isoformat() + "Z",
            "expires_at":
            self.expires_at.isoformat() + "Z" if self.expires_at else None,
        }

        if self.event_id:
            data["event_id"] = self.event_id

        if self.sender_id and self.sender:
            data["sender_name"] = self.sender.name
        if self.event_id and self.event:
            data["event_name"] = self.event.name

        return SerializedAnnouncement(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate announcement data. Raises ValidationError on failure
        """
        validator = BaseValidator()

        validator.validate_enum(
            data,
            "type",
            AnnouncementType,
            required = True,
            friendly_name = "Announcement type"
        )

        validator.validate_string(
            data,
            "title",
            max_length = config.NOTIFICATIONS_TITLE_MAX_LENGTH,
            required = True,
            friendly_name = "Title"
        )
        validator.validate_string(
            data,
            "message",
            max_length = config.NOTIFICATIONS_MESSAGE_MAX_LENGTH,
            required = True,
            friendly_name = "Message"
        )

        validator.validate_model_id(
            data,
            "sender_id",
            "Users",
            required = False
        )
        validator.validate_model_id(data, "event_id", "Event", required = False)
        validator.validate_datetime(
            data,
            "expires_at",
            required = False,
            friendly_name = "Expiration time"
        )

        return validator.validate()

    @classmethod
    def create_announcement(
        cls,
        announcement_type: AnnouncementType,
        title: str,
        message: str,
        *,
        sender_id: int | None = None,
        event_id: int | None = None,
        expires_at: Any | None = None,
        commit: bool = True,
    ) -> Announcement:
        """
        Create a new system announcement

        Args:
            announcement_type: Type of announcement
            title: Announcement title
            message: Announcement message
            sender_id: Admin user ID creating announcement
            event_id: Related event ID (for event-specific announcements)
            expires_at: When announcement expires
            commit: Whether to commit immediately

        Returns:
            Announcement: The created announcement instance
        """
        validated_data = cls.validate(
            {
                "type": announcement_type,
                "title": title,
                "message": message,
                "sender_id": sender_id,
                "event_id": event_id,
                "expires_at": expires_at,
            }
        )

        announcement = cls(
            type = validated_data["type"],
            title = validated_data["title"],
            message = validated_data["message"],
            sender_id = validated_data.get("sender_id"),
            event_id = validated_data.get("event_id"),
            expires_at = validated_data.get("expires_at"),
        )

        db.session.add(announcement)
        if commit:
            db.session.commit()
        return announcement

    @classmethod
    def find_by_id(cls, announcement_id: int) -> Announcement | None:
        """
        Find an announcement by ID
        """
        return cls.query.get(announcement_id)

    @classmethod
    def get_all_announcements(cls) -> list[Announcement]:
        """
        Get all announcements ordered by newest first
        """
        return cls.query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_active_announcements(
        cls,
        event_id: int | None = None,
    ) -> list[Announcement]:
        """
        Get active announcements (not expired)
        Args:
            event_id: Filter by event (None = global announcements)
        Returns:
            list[Announcement]: List of active announcements
        """
        query = cls.query.filter(
            (cls.expires_at.is_(None)) | (cls.expires_at > utc_now())
        )

        if event_id is not None:
            query = query.filter_by(event_id = event_id)
        else:
            query = query.filter(cls.event_id.is_(None))

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def delete_expired(cls) -> int:
        """
        Delete all expired announcements
        """
        count = cls.query.filter(cls.expires_at <= utc_now()).delete()

        db.session.commit()
        return count

    def delete(self, commit: bool = True) -> None:
        """
        Delete this announcement and cleanup associated notifications
        """
        Notification.query.filter_by(
            event_id = self.event_id if self.event_id else None
        ).filter(
            Notification.created_at == self.created_at,
            Notification.title == self.title,
            Notification.message == self.message,
        ).delete()

        db.session.delete(self)
        if commit:
            db.session.commit()