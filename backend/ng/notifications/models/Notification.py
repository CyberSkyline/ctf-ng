"""
Defines the Notification model for notifications
"""

from __future__ import annotations

from typing import (
    Any,
    TypedDict,
    NotRequired,
)
from enum import Enum

from CTFd.models import db

from ... import config
from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator


class NotificationType(str, Enum):
    TICKET_CREATE = "ticket_create"
    TICKET_MESSAGE = "ticket_message"
    TICKET_STATUS_CHANGE = "ticket_status_change"
    ATTEMPT_SUBMISSION = "attempt_submission"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    LEADERBOARD_UPDATE = "leaderboard_update"
    EVENT_UPDATE = "event_update"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class SerializedNotification(TypedDict):
    id: int
    type: str
    priority: str
    title: str
    message: str
    data: dict[str, Any] | None
    recipient_id: int | None
    sender_id: int | None
    read: bool
    created_at: str
    # Optional reference fields
    ticket_id: NotRequired[int | None]
    team_id: NotRequired[int | None]
    event_id: NotRequired[int | None]
    challenge_id: NotRequired[int | None]


class Notification(db.Model):
    __tablename__ = "ng_notifications"

    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.Enum(NotificationType), nullable = False)
    priority = db.Column(
        db.Enum(NotificationPriority),
        default = NotificationPriority.NORMAL,
        nullable = False
    )
    title = db.Column(db.String(config.NOTIFICATION_TITLE_MAX_LENGTH), nullable = False)
    message = db.Column(
        db.String(config.NOTIFICATION_MESSAGE_MAX_LENGTH),
        nullable = False
    )
    data = db.Column(db.JSON, nullable = True)

    recipient_id = db.Column(db.Integer,
                             db.ForeignKey("users.id"),
                             nullable = True,
                             index = True)  # None = broadcast
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = True)
    read = db.Column(db.Boolean, default = False, nullable = False)
    created_at = db.Column(db.DateTime, default = utc_now, nullable = False)

    ticket_id = db.Column(db.Integer, db.ForeignKey("ng_tickets.id"), nullable = True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable = True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable = True)
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_challenges.id"),
        nullable = True
    )

    __table_args__ = (
        db.Index("ix_ng_notifications_recipient_read",
                 "recipient_id",
                 "read"),
        db.Index("ix_ng_notifications_created",
                 "created_at"),
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

    def __repr__(self):
        return f"<Notification {self.id}: type={self.type.value} recipient={self.recipient_id}>"

    def serialize(self, include_admin_fields: bool = False) -> SerializedNotification:
        """
        Serialize notification for API response

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized notification data
        """
        data = {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "recipient_id": self.recipient_id,
            "sender_id": self.sender_id,
            "read": self.read,
            "created_at": self.created_at.isoformat() + "Z",
        }

        if self.ticket_id:
            data["ticket_id"] = self.ticket_id
        if self.team_id:
            data["team_id"] = self.team_id
        if self.event_id:
            data["event_id"] = self.event_id
        if self.challenge_id:
            data["challenge_id"] = self.challenge_id

        return SerializedNotification(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate notification data
        """
        validator = BaseValidator()

        validator.validate_enum(
            data,
            "type",
            NotificationType,
            required = True,
            friendly_name = "Notification type"
        )
        validator.validate_enum(
            data,
            "priority",
            NotificationPriority,
            required = False,
            friendly_name = "Priority"
        )

        validator.validate_string(
            data,
            "title",
            max_length = config.NOTIFICATION_TITLE_MAX_LENGTH,
            required = True,
            friendly_name = "Title"
        )
        validator.validate_string(
            data,
            "message",
            max_length = config.NOTIFICATION_MESSAGE_MAX_LENGTH,
            required = True,
            friendly_name = "Message"
        )

        validator.validate_model_id(data, "recipient_id", "Users", required = False)
        validator.validate_model_id(data, "sender_id", "Users", required = False)
        validator.validate_model_id(data, "ticket_id", "Ticket", required = False)
        validator.validate_model_id(data, "team_id", "Team", required = False)
        validator.validate_model_id(data, "event_id", "Event", required = False)
        validator.validate_model_id(data, "challenge_id", "Challenge", required = False)

        return validator.validate()

    @classmethod
    def create_notification(
        cls,
        notification_type: NotificationType,
        title: str,
        message: str,
        recipient_id: int | None = None,
        sender_id: int | None = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: dict[str,
                   Any] | None = None,
        ticket_id: int | None = None,
        team_id: int | None = None,
        event_id: int | None = None,
        challenge_id: int | None = None,
        commit: bool = True,
    ) -> Notification:
        """
        Create a new notification to the database

        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            recipient_id: User ID to receive notification (None for broadcast)
            sender_id: User ID sending notification
            priority: Notification priority
            data: Additional data payload
            ticket_id: Related ticket ID
            team_id: Related team ID
            event_id: Related event ID
            challenge_id: Related challenge ID
            commit: Whether to commit immediately

        Returns:
            Notification: The created notification instance
        """
        validated_data = cls.validate(
            {
                "type": notification_type,
                "title": title,
                "message": message,
                "priority": priority,
                "recipient_id": recipient_id,
                "sender_id": sender_id,
                "ticket_id": ticket_id,
                "team_id": team_id,
                "event_id": event_id,
                "challenge_id": challenge_id,
            }
        )

        notification = cls(
            type = validated_data["type"],
            title = validated_data["title"],
            message = validated_data["message"],
            priority = validated_data.get("priority",
                                          NotificationPriority.NORMAL),
            data = data,
            recipient_id = validated_data.get("recipient_id"),
            sender_id = validated_data.get("sender_id"),
            ticket_id = validated_data.get("ticket_id"),
            team_id = validated_data.get("team_id"),
            event_id = validated_data.get("event_id"),
            challenge_id = validated_data.get("challenge_id"),
        )

        db.session.add(notification)
        if commit:
            db.session.commit()
        return notification

    def mark_as_read(self, commit: bool = True) -> None:
        """
        Mark notification as read
        """
        self.read = True
        if commit:
            db.session.commit()

    @classmethod
    def find_filtered_notifications(
        cls,
        recipient_id: int | None = None,
        read_status: bool | None = None,
        notification_type: NotificationType | None = None,
        is_broadcast: bool | None = None,
        limit: int | None = None,
    ) -> list[Notification]:
        """
        Find notifications based on filters

        Args:
            recipient_id (int, optional): Filter by recipient user ID
            read_status (bool, optional): Filter by read status
            notification_type (NotificationType, optional): Filter by type
            is_broadcast (bool, optional): Filter broadcasts (recipient_id=None)
            limit (int, optional): Maximum number of results

        Returns:
            list[Notification]: List of filtered notifications
        """
        query = cls.query

        if recipient_id is not None:
            query = query.filter_by(recipient_id = recipient_id)
        if is_broadcast is True:
            query = query.filter(cls.recipient_id.is_(None))
        if read_status is not None:
            query = query.filter_by(read = read_status)
        if notification_type is not None:
            query = query.filter_by(type = notification_type)

        query = query.order_by(cls.created_at.desc())

        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @classmethod
    def find_by_id(cls, notification_id: int) -> Notification | None:
        """
        Find a notification by its ID

        Args:
            notification_id: The notification ID to search for

        Returns:
            Notification | None: The notification if found, None otherwise
        """
        return cls.query.get(notification_id)

    @classmethod
    def delete_all(cls) -> None:
        """
        Delete all notifications from the database
        """
        try:
            cls.query.delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
