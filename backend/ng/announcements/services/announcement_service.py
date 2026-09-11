"""
Service for handling announcement (system-wide and event-specific)
"""

from enum import Enum
from CTFd.models import Users, db

from ...core.utils import utc_now
from ...core.utils.emitters import emit_event, emit_to_users

from ...team.models import TeamMember
from ...notifications.models import (
    Notification,
    NotificationType,
)
from ...notifications.services.notification_service import WebSocketEvent

from ..models import Announcement, AnnouncementType


class AnnouncementWebSocketEvent(str, Enum):
    """
    Enum for announcement specific WebSocket event names
    """
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class AnnouncementService:
    """
    Service for creating and broadcasting announcements
    """
    @staticmethod
    def send_event_announcement(
        event_id: int,
        announcement_type: AnnouncementType,
        title: str,
        message: str,
        sender_id: int | None = None,
        expires_at: str | None = None,
        send_notification: bool = False,
    ) -> Announcement:
        """
        Send announcement to all event participants
        """
        announcement = Announcement.create_announcement(
            announcement_type = announcement_type,
            title = title,
            message = message,
            event_id = event_id,
            sender_id = sender_id,
            expires_at = expires_at,
        )

        if send_notification:
            user_ids = [
                row.user_id for row in
                TeamMember.query.with_entities(TeamMember.user_id)
                .filter_by(event_id = event_id)
            ]

            now = utc_now()
            # Avoids revalidating every foreign key once per participant
            db.session.bulk_insert_mappings(
                Notification,
                [
                    {
                        "type": NotificationType.EVENT_ANNOUNCEMENT,
                        "title": title,
                        "message": message,
                        "recipient_id": user_id,
                        "sender_id": sender_id,
                        "event_id": event_id,
                        "announcement_id": announcement.id,
                        "created_at": now,
                    }
                    for user_id in user_ids
                ]
            )
            db.session.commit()

            emit_to_users(WebSocketEvent.NOTIFICATION, {}, user_ids)

        return announcement

    @staticmethod
    def send_system_announcement(
        title: str,
        message: str,
        sender_id: int | None = None,
        expires_at: str | None = None,
        send_notification: bool = False,
    ) -> Announcement:
        """
        Send system wide announcement to all users

        Args:
            title: Announcement title
            message: Announcement message
            sender_id: ID of announcement sender
            expires_at: Optional expiration datetime
            send_notification: Whether to notify every user that is not banned

        Returns:
            Created Announcement object
        """
        announcement = Announcement.create_announcement(
            announcement_type = AnnouncementType.GENERAL,
            title = title,
            message = message,
            sender_id = sender_id,
            expires_at = expires_at,
        )

        if send_notification:
            user_ids = [
                row.id for row in
                Users.query.with_entities(Users.id).filter(Users.banned.isnot(True))
            ]

            now = utc_now()
            # Avoids revalidating every foreign key once per user
            db.session.bulk_insert_mappings(
                Notification,
                [
                    {
                        "type": NotificationType.EVENT_ANNOUNCEMENT,
                        "title": title,
                        "message": message,
                        "recipient_id": user_id,
                        "sender_id": sender_id,
                        "announcement_id": announcement.id,
                        "created_at": now,
                    }
                    for user_id in user_ids
                ]
            )
            db.session.commit()

            emit_event(
                event_name = WebSocketEvent.NOTIFICATION,
                data = {},
                user_ids = None  # Broadcast
            )

        emit_event(
            event_name = AnnouncementWebSocketEvent.SYSTEM_ANNOUNCEMENT,
            data = {
                "title": title,
                "message": message,
            },
            user_ids = None  # Broadcast
        )

        return announcement
