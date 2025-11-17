"""
Notification service for DB notifications and WebSocket refetch events
"""

from enum import Enum
from CTFd.models import db

from ...core.utils.emitters import (
    emit_to_user,
    emit_to_users,
    emit_to_team,
    emit_to_event,
    emit_to_admins,
)
from ...permissions.controllers import get_support_role_users

from ..models import Notification, NotificationType


class WebSocketEvent(str, Enum):
    """
    Enum for WebSocket event names for type safety
    """
    REFETCH = "refetch"
    NOTIFICATION = "notification"


class NotificationService:
    """
    Service for DB notifications and WebSocket refetch events
    """

    @staticmethod
    def _emit_refetch(
        path: str,
        user_ids=None,
        team_id=None,
        event_id=None
    ):
        """
        Notify frontend to refetch data at path
        """
        try:
            if user_ids:
                emit_to_users(WebSocketEvent.REFETCH, {"path": path}, user_ids)
            elif team_id:
                emit_to_team(WebSocketEvent.REFETCH, {"path": path}, team_id)
            elif event_id:
                emit_to_event(WebSocketEvent.REFETCH, {"path": path}, event_id)
            else:
                # Fallback to admin broadcast
                emit_to_admins(WebSocketEvent.REFETCH, {"path": path})

        except Exception:
            pass

    @staticmethod
    def _emit_notification(notification: Notification) -> None:
        """
        Send WebSocket event for a new notification to specific user
        """
        emit_to_user(
            WebSocketEvent.NOTIFICATION,
            notification.serialize(),
            user_id=notification.recipient_id
        )

    @staticmethod
    def notify_ticket_reply(
        ticket_id: int,
        author_id: int,
        recipient_id: int,
        is_admin_reply: bool = False,
    ) -> None:
        """
        Notify about support ticket reply (DB notification + WebSocket)
        """
        notification = Notification.create_notification(
            notification_type=NotificationType.TICKET_MESSAGE,
            title="Support Ticket Update",
            message=f"{'Admin' if is_admin_reply else 'User'} replied to your ticket",
            recipient_id=recipient_id,
            sender_id=author_id,
            ticket_id=ticket_id,
        )

        NotificationService._emit_notification(notification)

        NotificationService._emit_refetch(
            path=f"/ng/support/tickets/{ticket_id}",
            user_ids=[recipient_id, author_id]
        )

    @staticmethod
    def notify_ticket_status_change(
        ticket_id: int,
        recipient_id: int,
        new_status: str,
        changed_by_id: int,
    ) -> None:
        """
        Notify about ticket status change (DB notification only, no email)
        """
        notification = Notification.create_notification(
            notification_type=NotificationType.TICKET_STATUS_CHANGE,
            title="Ticket Status Changed",
            message=f"Your ticket was {new_status}",
            recipient_id=recipient_id,
            sender_id=changed_by_id,
            ticket_id=ticket_id,
        )

        NotificationService._emit_notification(notification)

        NotificationService._emit_refetch(
            path=f"/ng/support/tickets/{ticket_id}",
            user_ids=[recipient_id]
        )

    @staticmethod
    def notify_new_ticket(
        ticket_id: int,
        author_id: int,
        subject: str,
    ) -> None:
        """
        Notify admins about a new support ticket (WebSocket refetch only, no DB notifications)
        """
        NotificationService._emit_refetch(
            path="/ng/support/tickets",
        )

    @staticmethod
    def notify_unassigned_ticket_reply(
        ticket_id: int,
        author_id: int,
    ) -> None:
        """
        Notify all support staff when user replies to unassigned ticket
        """
        support_users = get_support_role_users()

        for support_user in support_users:
            notification = Notification.create_notification(
                notification_type=NotificationType.TICKET_MESSAGE,
                title="Support Ticket Update",
                message="User replied to unassigned ticket",
                recipient_id=support_user.ctfd_user.id,
                sender_id=author_id,
                ticket_id=ticket_id,
                commit=False,
            )

            NotificationService._emit_notification(notification)

        db.session.commit()

        NotificationService._emit_refetch(
            path=f"/ng/support/tickets/{ticket_id}",
        )

    @staticmethod
    def handle_ticket_message_notifications(
        ticket,
        message,
        author_id: int,
        is_admin: bool,
    ) -> None:
        """
        Handle all notifications for ticket messages (replies)
        Centralizes branching logic for ticket reply notifications

        Args:
            ticket: Ticket object
            message: TicketMessage object
            author_id: ID of message author
            is_admin: Whether author is admin
        """
        # Skip all notifications if ticket is muted
        if ticket.muted:
            return

        if is_admin:
            # Admin replying to user's ticket
            if ticket.author_id != author_id:
                NotificationService.notify_ticket_reply(
                    ticket_id=ticket.id,
                    author_id=author_id,
                    recipient_id=ticket.author_id,
                    is_admin_reply=True,
                )
        else:
            # User replying to ticket
            if ticket.assigned_to:
                # Assigned ticket - notify only assigned admin
                NotificationService.notify_ticket_reply(
                    ticket_id=ticket.id,
                    author_id=author_id,
                    recipient_id=ticket.assigned_to,
                    is_admin_reply=False,
                )
            else:
                # Unassigned ticket - notify all support staff
                NotificationService.notify_unassigned_ticket_reply(
                    ticket_id=ticket.id,
                    author_id=author_id,
                )

    @staticmethod
    def notify_ticket_assigned(
        ticket_id: int,
        assigned_to_id: int,
        assigned_by_id: int,
    ) -> None:
        """
        Notify admin when ticket is assigned to them (DB notification only, no email)
        """
        notification = Notification.create_notification(
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Ticket Assigned",
            message="A support ticket has been assigned to you",
            recipient_id=assigned_to_id,
            sender_id=assigned_by_id,
            ticket_id=ticket_id,
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
            path=f"/ng/events/{event_id}/challenges/{challenge_id}",
            team_id=team_id
        )

        NotificationService._emit_refetch(
            path=f"/ng/events/{event_id}/leaderboard",
            event_id=event_id
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
            path=f"/ng/events/{event_id}/challenges/{challenge_id}",
            team_id=team_id
        )

    @staticmethod
    def broadcast_team_update(
        team_id: int,
        update_type: str,
    ) -> None:
        """
        Broadcast team changes to team members
        """
        NotificationService._emit_refetch(
            path=f"/ng/teams/{team_id}",
            team_id=team_id
        )

    @staticmethod
    def notify_player_kicked_from_team(
        kicked_user_id: int,
        team_id: int,
        team_name: str,
        event_id: int,
        event_name: str,
        kicked_by_id: int | None = None,
    ) -> None:
        """
        Notify player when they are kicked from a team (DB notification + Email)

        Args:
            kicked_user_id: ID of the user who was kicked
            team_id: ID of the team they were kicked from
            team_name: Name of the team
            event_id: ID of the event
            event_name: Name of the event
            kicked_by_id: ID of the user who kicked them (admin or captain)
        """
        from ...emails.services.email_notification_service import TicketEmailService

        notification = Notification.create_notification(
            notification_type=NotificationType.TEAM_MEMBER_KICKED,
            title="Removed from Team",
            message=f"You have been removed from team '{team_name}' in event '{event_name}'",
            recipient_id=kicked_user_id,
            sender_id=kicked_by_id,
            team_id=team_id,
            event_id=event_id,
        )

        NotificationService._emit_notification(notification)

        TicketEmailService.send_player_kicked_email(
            kicked_user_id=kicked_user_id,
            team_name=team_name,
            event_name=event_name,
            event_id=event_id,
            kicked_by_id=kicked_by_id,
        )