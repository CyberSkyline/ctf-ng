"""
Service for handling announcements (system-wide and event-specific)
"""

from enum import Enum
from CTFd.models import db

from ...core.utils.emitters import emit_event

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
    ) -> Announcement:
        """
        Send announcement to all event participants

        Args:
            event_id: Event ID
            announcement_type: Type of announcement
            title: Announcement title
            message: Announcement message
            sender_id: ID of announcement sender

        Returns:
            Created Announcement object
        """
        announcement = Announcement.create_announcement(
            announcement_type = announcement_type,
            title = title,
            message = message,
            event_id = event_id,
            sender_id = sender_id,
        )

        participants = TeamMember.query.filter_by(event_id = event_id).all()
        participant_user_ids = [member.user_id for member in participants]

        for user_id in participant_user_ids:
            notification = Notification.create_notification(
                notification_type = NotificationType.EVENT_ANNOUNCEMENT,
                title = title,
                message = message,
                recipient_id = user_id,
                sender_id = sender_id,
                event_id = event_id,
                commit = False,
            )
            NotificationService._emit_notification(notification)

        db.session.commit()

        NotificationService._emit_refetch(
            path = f"/ng/events/{event_id}/announcements",
            event_id = event_id
        )

        return announcement

    @staticmethod
    def send_system_announcement(
        title: str,
        message: str,
        sender_id: int | None = None,
    ) -> Announcement:
        """
        Send system wide announcement to all connected users

        Args:
            title: Announcement title
            message: Announcement message
            sender_id: ID of announcement sender

        Returns:
            Created Announcement object
        """
        announcement = Announcement.create_announcement(
            announcement_type = AnnouncementType.GENERAL,
            title = title,
            message = message,
            sender_id = sender_id,
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
