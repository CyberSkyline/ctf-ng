"""
Notification service handling both stored
notifications and WebSocket refetch events
"""

from CTFd.models import db

from ...core.utils.emitters import (
    emit_to_user,
    emit_to_users,
    emit_to_team,
    emit_to_event,
    emit_to_admins,
    emit_event
)

from ..models import (
    Notification,
    NotificationType,
    Announcement,
    AnnouncementType,
)
from ...team.models import TeamMember


class NotificationService:
    """
    Stored notifications & WebSocket refetch events using Redis pub/sub
    """
    @staticmethod
    def _emit_refetch(
        path: str,
        user_ids = None,
        team_id = None,
        event_id = None
    ):
        """
        Notify frontend to refetch data at path
        """
        try:
            if user_ids:
                emit_to_users("refetch", {"path": path}, user_ids)
            elif team_id:
                emit_to_team("refetch", {"path": path}, team_id)
            elif event_id:
                emit_to_event("refetch", {"path": path}, event_id)
            else:
                # Fallback to admin broadcast
                emit_to_admins("refetch", {"path": path})

        except Exception:
            pass

    @staticmethod
    def _emit_notification(notification: Notification) -> None:
        """
        Send WebSocket event for a new notification to specific user
        """
        emit_to_user(
            "notification",
            notification.serialize(),
            user_id = notification.recipient_id
        )

    @staticmethod
    def notify_ticket_reply(
        ticket_id: int,
        author_id: int,
        recipient_id: int,
        is_admin_reply: bool = False,
    ) -> None:
        """
        Notify about support ticket reply
        """
        notification = Notification.create_notification(
            notification_type = NotificationType.TICKET_MESSAGE,
            title = "Support Ticket Update",
            message =
            f"{'Admin' if is_admin_reply else 'User'} replied to your ticket",
            recipient_id = recipient_id,
            sender_id = author_id,
            ticket_id = ticket_id,
        )

        NotificationService._emit_notification(notification)

        NotificationService._emit_refetch(
            path = f"/ng/support/tickets/{ticket_id}",
            user_ids = [recipient_id,
                        author_id]
        )

    @staticmethod
    def notify_ticket_status_change(
        ticket_id: int,
        recipient_id: int,
        new_status: str,
        changed_by_id: int,
    ) -> None:
        """
        Notify about ticket status change
        """
        notification = Notification.create_notification(
            notification_type = NotificationType.TICKET_STATUS_CHANGE,
            title = "Ticket Status Changed",
            message = f"Your ticket was {new_status}",
            recipient_id = recipient_id,
            sender_id = changed_by_id,
            ticket_id = ticket_id,
        )

        NotificationService._emit_notification(notification)

        NotificationService._emit_refetch(
            path = f"/ng/support/tickets/{ticket_id}",
            user_ids = [recipient_id]
        )

    @staticmethod
    def notify_new_ticket(
        ticket_id: int,
        author_id: int,
        subject: str,
    ) -> None:
        """
        Notify admins about a new support ticket
        """
        NotificationService._emit_refetch(
            path = "/ng/support/tickets",
            user_ids = None  # Via _emit_refetch fallback
        )

    @staticmethod
    def notify_ticket_assigned(
        ticket_id: int,
        assigned_to_id: int,
        assigned_by_id: int,
    ) -> None:
        """
        Notify admin when ticket is assigned to them
        """
        notification = Notification.create_notification(
            notification_type = NotificationType.TICKET_ASSIGNED,
            title = "Ticket Assigned",
            message = "A support ticket has been assigned to you",
            recipient_id = assigned_to_id,
            sender_id = assigned_by_id,
            ticket_id = ticket_id,
        )

        NotificationService._emit_notification(notification)

    @staticmethod
    def broadcast_attempt_update(
        event_id: int,
        team_id: int,
        challenge_id: int,
        question_id: int,
    ) -> None:
        """
        Broadcast attempt submission to team members and event leaderboard update
        """
        NotificationService._emit_refetch(
            path = f"/ng/events/{event_id}/challenges/{challenge_id}",
            team_id = team_id
        )

        NotificationService._emit_refetch(
            path = f"/ng/events/{event_id}/leaderboard",
            event_id = event_id
        )

    @staticmethod
    def broadcast_hint_redeemed(
        event_id: int,
        team_id: int,
        challenge_id: int,
    ) -> None:
        """
        Broadcast hint redemption to team members
        """
        NotificationService._emit_refetch(
            path = f"/ng/events/{event_id}/challenges/{challenge_id}",
            team_id = team_id
        )

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
        """
        announcement = Announcement.create_announcement(
            announcement_type = AnnouncementType.GENERAL,
            title = title,
            message = message,
            sender_id = sender_id,
        )

        emit_event(
            event_name = "system_announcement",
            data = {
                "title": title,
                "message": message,
            },
            user_ids = None  # Broadcast
        )

        return announcement

    @staticmethod
    def notify_team_invitation(
        team_id: int,
        team_name: str,
        invited_user_id: int,
        invited_by_id: int,
    ) -> None:
        """
        Notify user about team invitation
        """
        notification = Notification.create_notification(
            notification_type = NotificationType.TEAM_INVITATION,
            title = "Team Invitation",
            message = f"You've been invited to join team '{team_name}'",
            recipient_id = invited_user_id,
            sender_id = invited_by_id,
            team_id = team_id,
        )

        NotificationService._emit_notification(notification)

    @staticmethod
    def broadcast_team_update(
        team_id: int,
        update_type: str,
    ) -> None:
        """
        Broadcast team changes to team members
        """
        NotificationService._emit_refetch(
            path = f"/ng/teams/{team_id}",
            team_id = team_id
        )

    @staticmethod
    def notify_challenge_released(
        event_id: int,
        challenge_id: int,
        challenge_name: str,
    ) -> None:
        """
        Notify participants about new challenge
        """
        participants = TeamMember.query.filter_by(event_id = event_id).all()
        participant_user_ids = [member.user_id for member in participants]

        for user_id in participant_user_ids:
            notification = Notification.create_notification(
                notification_type = NotificationType.CHALLENGE_RELEASED,
                title = "New Challenge Available",
                message = f"Challenge '{challenge_name}' is now available",
                recipient_id = user_id,
                event_id = event_id,
                challenge_id = challenge_id,
                commit = False,
            )
            NotificationService._emit_notification(notification)

        db.session.commit()

        NotificationService._emit_refetch(
            path = f"/ng/events/{event_id}/challenges",
            event_id = event_id
        )
