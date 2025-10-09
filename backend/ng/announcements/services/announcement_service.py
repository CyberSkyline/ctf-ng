"""
Service for handling announcement (system-wide and event-specific)
"""

from enum import Enum
from CTFd.models import db

from ...core.utils.emitters import emit_event
from ...notifications.sockets import get_connected_users

from ...team.models import TeamMember
from ...notifications.models import (
    Notification,
    NotificationType,
)
from ...notifications.services.notification_service import (
    NotificationService,
)

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
        send_notification: bool = True,
    ) -> Announcement:
        """
        Send announcement to all event participants
        """
        announcement = Announcement.create_announcement(
            announcement_type=announcement_type,
            title=title,
            message=message,
            event_id=event_id,
            sender_id=sender_id,
            expires_at=expires_at,
        )

        if send_notification:
            participants = TeamMember.query.filter_by(event_id=event_id).all()
            participant_user_ids = [member.user_id for member in participants]

            for user_id in participant_user_ids:
                notification = Notification.create_notification(
                    notification_type=NotificationType.EVENT_ANNOUNCEMENT,
                    title=title,
                    message=message,
                    recipient_id=user_id,
                    sender_id=sender_id,
                    event_id=event_id,
                    commit=False,
                )
                NotificationService._emit_notification(notification)

            db.session.commit()

        NotificationService._emit_refetch(
            path=f"/ng/events/{event_id}/announcements",
            event_id=event_id
        )

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
        Send system wide announcement to all connected users

        Args:
            title: Announcement title
            message: Announcement message
            sender_id: ID of announcement sender
            expires_at: Optional expiration datetime
            send_notification: Whether to send notification to connected users

        Returns:
            Created Announcement object
        """
        announcement = Announcement.create_announcement(
            announcement_type=AnnouncementType.GENERAL,
            title=title,
            message=message,
            sender_id=sender_id,
            expires_at=expires_at,
        )

        if send_notification:
            connected_user_ids = get_connected_users()

            for user_id in connected_user_ids:
                notification = Notification.create_notification(
                    notification_type=NotificationType.EVENT_ANNOUNCEMENT,
                    title=title,
                    message=message,
                    recipient_id=user_id,
                    sender_id=sender_id,
                    commit=False,
                )
                NotificationService._emit_notification(notification)

            if connected_user_ids:
                db.session.commit()

        emit_event(
            event_name=AnnouncementWebSocketEvent.SYSTEM_ANNOUNCEMENT,
            data={
                "title": title,
                "message": message,
            },
            user_ids=None  # Broadcast
        )

        return announcement
