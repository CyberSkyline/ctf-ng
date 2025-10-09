"""
Defines the Notification model for user-specific notifications
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


class NotificationType(str, Enum):
    TICKET_CREATE = "ticket_create"
    TICKET_MESSAGE = "ticket_message"
    TICKET_STATUS_CHANGE = "ticket_status_change"
    TICKET_ASSIGNED = "ticket_assigned"
    CHALLENGE_UPDATED = "challenge_updated"
    EVENT_ANNOUNCEMENT = "event_announcement"


class SerializedNotification(TypedDict):
    id: int
    type: str
    title: str
    message: str
    recipient_id: int
    sender_id: int | None
    read_at: str | None
    created_at: str
    expires_at: str | None
    # Optional reference fields
    ticket_id: NotRequired[int | None]
    team_id: NotRequired[int | None]
    event_id: NotRequired[int | None]
    challenge_id: NotRequired[int | None]
    # Name enrichment fields
    recipient_name: NotRequired[str]
    sender_name: NotRequired[str | None]
    ticket_subject: NotRequired[str | None]
    team_name: NotRequired[str | None]
    event_name: NotRequired[str | None]
    challenge_name: NotRequired[str | None]


class Notification(db.Model):
    __tablename__ = "ng_notifications"

    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.Enum(NotificationType), nullable = False)
    title = db.Column(
        db.String(config.NOTIFICATIONS_TITLE_MAX_LENGTH),
        nullable = False
    )
    message = db.Column(
        db.String(config.NOTIFICATIONS_MESSAGE_MAX_LENGTH),
        nullable = False
    )

    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable = False,
        index = True
    )
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable = True
    )
    read_at = db.Column(db.DateTime, nullable = True)
    created_at = db.Column(db.DateTime, default = utc_now, nullable = False)
    expires_at = db.Column(db.DateTime, nullable = True)

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_tickets.id"),
        nullable = True
    )
    team_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_teams.id"),
        nullable = True
    )
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_events.id"),
        nullable = True
    )
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_challenges.id"),
        nullable = True
    )

    __table_args__ = (
        db.Index(
            "ix_ng_notifications_recipient_read",
            "recipient_id",
            "read_at"
        ),
        db.Index("ix_ng_notifications_created",
                 "created_at"),
        db.Index("ix_ng_notifications_expires",
                 "expires_at"),
    )

    recipient = db.relationship(
        "Users",
        foreign_keys = [recipient_id],
        backref = "notifications_received"
    )
    sender = db.relationship(
        "Users",
        foreign_keys = [sender_id],
        backref = "notifications_sent"
    )
    ticket = db.relationship("Ticket", backref="notifications")
    team = db.relationship("Team", backref="notifications")
    event = db.relationship("Event", backref="notifications")
    challenge = db.relationship("Challenge", backref="notifications")

    def __repr__(self):
        return f"<Notification {self.id}: type={self.type.value} recipient={self.recipient_id}>"

    @property
    def is_read(self) -> bool:
        """
        Check if notification has been read
        """
        return self.read_at is not None

    def serialize(
        self,
        include_admin_fields: bool = False
    ) -> SerializedNotification:
        """
        Serialize notification for API response

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized notification data
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
            "recipient_id":
            self.recipient_id,
            "sender_id":
            self.sender_id,
            "read_at":
            self.read_at.isoformat() + "Z" if self.read_at else None,
            "created_at":
            self.created_at.isoformat() + "Z",
            "expires_at":
            self.expires_at.isoformat() + "Z" if self.expires_at else None,
        }

        if self.ticket_id:
            data["ticket_id"] = self.ticket_id
        if self.team_id:
            data["team_id"] = self.team_id
        if self.event_id:
            data["event_id"] = self.event_id
        if self.challenge_id:
            data["challenge_id"] = self.challenge_id

        if self.recipient:
            data["recipient_name"] = self.recipient.name
        if self.sender_id and self.sender:
            data["sender_name"] = self.sender.name
        if self.ticket_id and self.ticket:
            data["ticket_subject"] = self.ticket.subject
        if self.team_id and self.team:
            data["team_name"] = self.team.name
        if self.event_id and self.event:
            data["event_name"] = self.event.name
        if self.challenge_id and self.challenge:
            data["challenge_name"] = self.challenge.name

        return SerializedNotification(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate notification data. Raises ValidationError on failure
        """
        validator = BaseValidator()

        validator.validate_enum(
            data,
            "type",
            NotificationType,
            required = True,
            friendly_name = "Notification type"
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
            "recipient_id",
            "Users",
            required = True
        )
        validator.validate_model_id(
            data,
            "sender_id",
            "Users",
            required = False
        )
        validator.validate_model_id(
            data,
            "ticket_id",
            "Ticket",
            required = False
        )
        validator.validate_model_id(
            data,
            "team_id",
            "Team",
            required = False
        )
        validator.validate_model_id(
            data,
            "event_id",
            "Event",
            required = False
        )
        validator.validate_model_id(
            data,
            "challenge_id",
            "Challenge",
            required = False
        )

        validator.validate_datetime(
            data,
            "expires_at",
            required = False,
            friendly_name = "Expiration time"
        )

        return validator.validate()

    @classmethod
    def create_notification(
        cls,
        notification_type: NotificationType,
        title: str,
        message: str,
        recipient_id: int,
        *,
        sender_id: int | None = None,
        ticket_id: int | None = None,
        team_id: int | None = None,
        event_id: int | None = None,
        challenge_id: int | None = None,
        expires_at: Any | None = None,
        commit: bool = True,
    ) -> Notification:
        """
        Create a new user notification

        Args:
            type: Type of notification
            title: Notification title
            message: Notification message
            recipient_id: User ID to receive notification
            sender_id: User ID sending notification
            ticket_id: Related ticket ID
            team_id: Related team ID
            event_id: Related event ID
            challenge_id: Related challenge ID
            expires_at: When notification expires
            commit: Whether to commit immediately

        Returns:
            Notification: The created notification instance
        """
        validated_data = cls.validate(
            {
                "type": notification_type,
                "title": title,
                "message": message,
                "recipient_id": recipient_id,
                "sender_id": sender_id,
                "ticket_id": ticket_id,
                "team_id": team_id,
                "event_id": event_id,
                "challenge_id": challenge_id,
                "expires_at": expires_at,
            }
        )

        notification = cls(
            type = validated_data["type"],
            title = validated_data["title"],
            message = validated_data["message"],
            recipient_id = validated_data["recipient_id"],
            sender_id = validated_data.get("sender_id"),
            ticket_id = validated_data.get("ticket_id"),
            team_id = validated_data.get("team_id"),
            event_id = validated_data.get("event_id"),
            challenge_id = validated_data.get("challenge_id"),
            expires_at = validated_data.get("expires_at"),
            created_at = utc_now(),
        )

        db.session.add(notification)
        if commit:
            db.session.commit()
        return notification

    def mark_as_read(self, commit: bool = True) -> None:
        """
        Mark notification as read by setting read_at timestamp
        """
        if not self.read_at:
            self.read_at = utc_now()
            if commit:
                db.session.commit()

    @classmethod
    def find_by_id(cls, notification_id: int) -> Notification | None:
        """
        Find a notification by ID
        """
        return cls.query.get(notification_id)

    @classmethod
    def find_filtered_notifications(
        cls,
        recipient_id: int,
        is_read: bool | None = None,
        notification_type: NotificationType | None = None,
        expired: bool = False,
    ) -> list[Notification]:
        """
        Find notifications based on filters
        Args:
            recipient_id: Filter by recipient user ID
            is_read: Filter by read status (True = read, False = unread)
            notification_type: Filter by type
            expired: Include expired notifications (default False)
        Returns:
            list[Notification]: List of filtered notifications
        """
        query = cls.query.filter_by(recipient_id = recipient_id)

        if is_read is True:
            query = query.filter(cls.read_at.isnot(None))
        elif is_read is False:
            query = query.filter(cls.read_at.is_(None))

        if notification_type is not None:
            query = query.filter_by(type = notification_type)

        if not expired:
            query = query.filter(
                (cls.expires_at.is_(None)) | (cls.expires_at > utc_now())
            )

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_unread_count(cls, recipient_id: int) -> int:
        """
        Get count of unread notifications for a user
        """
        return cls.query.filter_by(recipient_id = recipient_id).filter(
            cls.read_at.is_(None)
        ).filter((cls.expires_at.is_(None))
                 | (cls.expires_at > utc_now())).count()

    @classmethod
    def mark_all_as_read(cls, recipient_id: int) -> int:
        """
        Mark all unread notifications as read for a user.
        Returns count of notifications updated.
        """
        count = cls.query.filter_by(
            recipient_id=recipient_id,
        ).filter(
            cls.read_at.is_(None)
        ).update(
            {"read_at": utc_now()}
        )
        db.session.commit()
        return count

    @classmethod
    def delete_expired(cls) -> int:
        """
        Delete all expired notifications
        """
        count = cls.query.filter(cls.expires_at <= utc_now()).delete()

        db.session.commit()
        return count
