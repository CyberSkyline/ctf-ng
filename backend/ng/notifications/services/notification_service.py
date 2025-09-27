"""
Notification service with email support for tickets
"""

from enum import Enum
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from CTFd.models import db, Users

from ...core.utils.emitters import (
    emit_to_user,
    emit_to_users,
    emit_to_team,
    emit_to_event,
    emit_to_admins,
    emit_event
)
from ...core.utils.logger import get_logger

from ..models import (
    Notification,
    NotificationType,
    Announcement,
    AnnouncementType,
)
from ...team.models import TeamMember
from ...support.models.Ticket import Ticket

from .email_service import get_email_service
from .email_templates import TicketEmailTemplates


logger = get_logger(__name__)


class WebSocketEvent(str, Enum):
    """
    Enum for WebSocket event names for type safety
    """
    REFETCH = "refetch"
    NOTIFICATION = "notification"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class EmailType(str, Enum):
    """
    Enum for email types for type safety
    """
    NEW_TICKET = "new_ticket"
    REPLY = "reply"
    ASSIGNED = "assigned"
    STATUS_CHANGE = "status_change"


class NotificationService:
    """
    Notification service with email support for tickets
    """
    @staticmethod
    def _get_admin_support_inbox_emails() -> list[str]:
        """
        Get admin support inbox emails for new unassigned tickets only
        """
        admin_emails = current_app.config.get(
            'ADMIN_SUPPORT_INBOX_EMAILS',
            ''
        )
        if not admin_emails:
            return []

        emails = [
            email.strip()
            for email in admin_emails.split(',')
            if email.strip()
        ]
        return emails

    @staticmethod
    def _get_user_email(user_id: int) -> str | None:
        """
        Get email for specific user
        """
        if user_id is None:
            return None
        try:
            user = Users.query.get(user_id)
            return user.email if user and user.email else None
        except SQLAlchemyError as e:
            logger.error(
                "Database error getting user email for user %s: %s",
                user_id,
                e
            )
            return None
        except Exception as e:
            logger.error(
                "Error getting user email for user %s: %s",
                user_id,
                e
            )
            return None

    @staticmethod
    def _get_team_member_emails(team_id: int) -> list[str]:
        """
        Get emails for all users in a team
        """
        try:
            team_members = TeamMember.query.filter_by(team_id = team_id
                                                      ).all()
            emails = []

            for member in team_members:
                if member.user and member.user.ctfd_user and member.user.ctfd_user.email:
                    emails.append(member.user.ctfd_user.email)

            return emails
        except SQLAlchemyError as e:
            logger.error(
                "Database error getting team member emails for team %s: %s",
                team_id,
                e
            )
            return []
        except Exception as e:
            logger.error(
                "Error getting team member emails for team %s: %s",
                team_id,
                e
            )
            return []

    @staticmethod
    def _build_email_recipients(ticket: Ticket,
                                email_type: EmailType,
                                **kwargs) -> list[str]:
        """
        Build email list based on ticket context and notification type

        Args:
            ticket: Ticket object with relationships
            email_type: Type of email (EmailType enum)
            **kwargs: Additional context like is_admin_reply, replying_admin_id

        Returns:
            list[str]: Deduplicated list of email addresses to notify
        """
        emails = set()

        if email_type == EmailType.NEW_TICKET:
            # Only admin support inbox for new unassigned tickets
            emails.update(
                NotificationService._get_admin_support_inbox_emails()
            )

        elif email_type == EmailType.REPLY:
            is_admin_reply = kwargs.get('is_admin_reply', False)

            if is_admin_reply:
                # Admin replying
                if ticket.team_id:
                    # Team ticket: notify all team members
                    emails.update(
                        NotificationService._get_team_member_emails(
                            ticket.team_id
                        )
                    )
                else:
                    # Non team ticket: notify just the ticket author
                    author_email = NotificationService._get_user_email(
                        ticket.author_id
                    )
                    if author_email:
                        emails.add(author_email)
            else:
                # User replying
                if ticket.assigned_to:
                    # Send to assigned admin
                    assigned_email = NotificationService._get_user_email(
                        ticket.assigned_to
                    )
                    if assigned_email:
                        emails.add(assigned_email)
                else:
                    # Unassigned ticket, send to admin support inbox
                    emails.update(
                        NotificationService._get_admin_support_inbox_emails()
                    )

        elif email_type == EmailType.STATUS_CHANGE:
            author_email = NotificationService._get_user_email(
                ticket.author_id
            )
            if author_email:
                emails.add(author_email)
            if ticket.team_id:
                emails.update(
                    NotificationService._get_team_member_emails(
                        ticket.team_id
                    )
                )
            if ticket.assigned_to:
                assigned_email = NotificationService._get_user_email(
                    ticket.assigned_to
                )
                if assigned_email:
                    emails.add(assigned_email)

        elif email_type == EmailType.ASSIGNED:
            assigned_to_id = kwargs.get('assigned_to_id', ticket.assigned_to)
            assigned_email = NotificationService._get_user_email(
                assigned_to_id
            )
            if assigned_email:
                emails.add(assigned_email)

        return [email for email in emails if email]

    @staticmethod
    def _send_ticket_email(
        ticket: Ticket,
        email_type: EmailType,
        additional_data: dict | None = None
    ) -> None:
        """
        Send ticket related email using smart routing

        Args:
            ticket: Ticket object with relationships
            email_type: Type of email (EmailType enum)
            additional_data: Additional data for specific email types
        """
        email_service = get_email_service()

        routing_context = {}
        if additional_data:
            routing_context.update(additional_data)

        recipient_emails = NotificationService._build_email_recipients(
            ticket,
            email_type,
            **routing_context
        )

        if not recipient_emails:
            logger.warning(
                "No recipient emails found for ticket %s, email type %s",
                ticket.id,
                email_type
            )
            return

        try:
            ticket_data = ticket.serialize(include_admin_fields = True)

            if email_type == EmailType.NEW_TICKET:
                subject, html_body, text_body = TicketEmailTemplates.new_ticket(
                    ticket_data)

            elif email_type == EmailType.REPLY:
                if additional_data is None:
                    return
                message_data = additional_data.get('message_data', {})
                is_admin_reply = additional_data.get('is_admin_reply', False)
                subject, html_body, text_body = TicketEmailTemplates.ticket_reply(
                    ticket_data, message_data, is_admin_reply)

            elif email_type == EmailType.STATUS_CHANGE:
                if additional_data is None:
                    return
                new_status = additional_data.get('new_status', 'updated')
                subject, html_body, text_body = TicketEmailTemplates.ticket_status_change(
                    ticket_data, new_status)

            elif email_type == EmailType.ASSIGNED:
                if additional_data is None:
                    return
                assigned_to_name = additional_data.get(
                    'assigned_to_name',
                    'Unknown'
                )
                subject, html_body, text_body = TicketEmailTemplates.ticket_assigned(
                    ticket_data, assigned_to_name)
            else:
                return

            email_service.send_email(
                to_emails = recipient_emails,
                subject = subject,
                html_body = html_body,
                text_body = text_body
            )

        except (SQLAlchemyError, ConnectionError) as e:
            logger.error(
                "Database or connection error sending ticket email: %s",
                e
            )
        except Exception as e:
            logger.error("Failed to send ticket email notification: %s", e)

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
                emit_to_users(
                    WebSocketEvent.REFETCH,
                    {"path": path},
                    user_ids
                )
            elif team_id:
                emit_to_team(WebSocketEvent.REFETCH, {"path": path}, team_id)
            elif event_id:
                emit_to_event(
                    WebSocketEvent.REFETCH,
                    {"path": path},
                    event_id
                )
            else:
                # Fallback to admin broadcast
                emit_to_admins(WebSocketEvent.REFETCH, {"path": path})

        except (ConnectionError, OSError) as e:
            logger.debug("WebSocket emit error (non-critical): %s", e)
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
        Notify about support ticket reply - with email
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

        try:
            ticket = Ticket.find_by_id(ticket_id)
            if ticket:
                messages = ticket.get_messages()
                latest_message = messages[-1] if messages else None

                if latest_message:
                    NotificationService._send_ticket_email(
                        ticket = ticket,
                        email_type = EmailType.REPLY,
                        additional_data = {
                            'message_data':
                            latest_message.serialize(
                                include_admin_fields = True
                            ),
                            'is_admin_reply':
                            is_admin_reply
                        }
                    )
        except SQLAlchemyError as e:
            logger.error(
                "Database error sending reply email notification: %s",
                e
            )
        except Exception as e:
            logger.error("Failed to send reply email notification: %s", e)

    @staticmethod
    def notify_ticket_status_change(
        ticket_id: int,
        recipient_id: int,
        new_status: str,
        changed_by_id: int,
    ) -> None:
        """
        Notify about ticket status change - with email
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

        try:
            ticket = Ticket.find_by_id(ticket_id)
            if ticket:
                NotificationService._send_ticket_email(
                    ticket = ticket,
                    email_type = EmailType.STATUS_CHANGE,
                    additional_data = {'new_status': new_status}
                )
        except SQLAlchemyError as e:
            logger.error(
                "Database error sending status change email notification: %s",
                e
            )
        except Exception as e:
            logger.error(
                "Failed to send status change email notification: %s",
                e
            )

    @staticmethod
    def notify_new_ticket(
        ticket_id: int,
        author_id: int,
        subject: str,
    ) -> None:
        """
        Notify admins about a new support ticket - with email
        """
        NotificationService._emit_refetch(
            path = "/ng/support/tickets",
            user_ids = None  # Via _emit_refetch fallback
        )

        try:
            ticket = Ticket.find_by_id(ticket_id)
            if ticket:
                NotificationService._send_ticket_email(
                    ticket = ticket,
                    email_type = EmailType.NEW_TICKET
                )
        except SQLAlchemyError as e:
            logger.error(
                "Database error sending new ticket email notification: %s",
                e
            )
        except Exception as e:
            logger.error(
                "Failed to send new ticket email notification: %s",
                e
            )

    @staticmethod
    def notify_ticket_assigned(
        ticket_id: int,
        assigned_to_id: int,
        assigned_by_id: int,
    ) -> None:
        """
        Notify admin when ticket is assigned to them - with email
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

        try:
            ticket = Ticket.find_by_id(ticket_id)
            assigned_user = Users.query.get(assigned_to_id)

            if ticket and assigned_user:
                NotificationService._send_ticket_email(
                    ticket = ticket,
                    email_type = EmailType.ASSIGNED,
                    additional_data = {
                        'assigned_to_name': assigned_user.name,
                        'assigned_to_id': assigned_to_id
                    }
                )
        except SQLAlchemyError as e:
            logger.error(
                "Database error sending assignment email notification: %s",
                e
            )
        except Exception as e:
            logger.error(
                "Failed to send assignment email notification: %s",
                e
            )

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
            event_name = WebSocketEvent.SYSTEM_ANNOUNCEMENT,
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
