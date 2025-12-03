"""
Service for sending ticket-related emails
"""

from enum import Enum

from CTFd.models import Users
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ...core.utils.logger import get_logger
from ...support.models.Ticket import Ticket
from ...team.models import TeamMember
from .email_sender import get_email_service
from .email_templates import TeamKickedData, TicketEmailTemplates

logger = get_logger(__name__)

server_domain = current_app.config.get('SERVER_DOMAIN')
route_prefix = current_app.config.get('ROUTE_PREFIX')
base_url = f"{server_domain}{route_prefix}"

class EmailType(str, Enum):
    """
    Enum for email types for type safety
    """
    NEW_TICKET = "new_ticket"
    REPLY = "reply"


class TicketEmailService:
    """
    Service for handling ticket-related email notifications
    """
    @staticmethod
    def _get_admin_support_inbox_emails() -> list[str]:
        """
        Get admin support inbox email/s from config
        """
        admin_emails = current_app.config.get('ADMIN_SUPPORT_INBOX_EMAILS', '')
        if not admin_emails:
            return []

        emails = [
            email.strip() for email in admin_emails.split(',') if email.strip()
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
            logger.error("Error getting user email for user %s: %s", user_id, e)
            return None

    @staticmethod
    def _get_team_member_emails(team_id: int) -> list[str]:
        """
        Get emails for all users in a team
        """
        try:
            team_members = TeamMember.query.filter_by(team_id = team_id).all()
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
            **kwargs: Additional context like is_admin_reply

        Returns:
            list[str]: Deduplicated list of email addresses to notify
        """
        emails = set()

        if email_type == EmailType.NEW_TICKET:
            # Only admin support inbox for new unassigned tickets
            emails.update(TicketEmailService._get_admin_support_inbox_emails())

        elif email_type == EmailType.REPLY:
            is_admin_reply = kwargs.get('is_admin_reply', False)

            if is_admin_reply:
                # Admin replying
                if ticket.team_id:
                    # Team ticket: notify all team members
                    emails.update(
                        TicketEmailService._get_team_member_emails(
                            ticket.team_id
                        )
                    )
                else:
                    # Non team ticket: notify just the ticket author
                    author_email = TicketEmailService._get_user_email(
                        ticket.author_id
                    )
                    if author_email:
                        emails.add(author_email)
            else:
                # User replying
                if ticket.assigned_to:
                    # Send to assigned admin
                    assigned_email = TicketEmailService._get_user_email(
                        ticket.assigned_to
                    )
                    if assigned_email:
                        emails.add(assigned_email)
                else:
                    # Unassigned ticket, send to admin support inbox
                    # NOTE: This is a fallback - admins get auto assigned upon initial reply
                    emails.update(
                        TicketEmailService._get_admin_support_inbox_emails()
                    )

        return [email for email in emails if email]

    @staticmethod
    def send_new_ticket_email(ticket: Ticket) -> None:
        """
        Send email notification for new ticket creation

        Args:
            ticket: Ticket object
        """
        email_service = get_email_service()

        recipient_emails = TicketEmailService._build_email_recipients(
            ticket,
            EmailType.NEW_TICKET
        )

        if not recipient_emails:
            logger.warning(
                "No recipient emails found for new ticket %s",
                ticket.id
            )
            return

        try:
            ticket_data = ticket.serialize(include_admin_fields = True)

            subject, html_body, text_body = TicketEmailTemplates.new_ticket(
                ticket_data
            )

            email_service.send_email(
                to_emails = recipient_emails,
                subject = subject,
                html_body = html_body,
                text_body = text_body
            )

        except SQLAlchemyError as e:
            logger.error("Database error sending new ticket email: %s", e)
        except Exception as e:
            logger.error("Failed to send new ticket email: %s", e)

    @staticmethod
    def send_ticket_reply_email(
        ticket: Ticket,
        message,
        is_admin_reply: bool
    ) -> None:
        """
        Send email notification for ticket reply

        Args:
            ticket: Ticket object
            message: TicketMessage object
            is_admin_reply: Whether this is an admin reply
        """
        email_service = get_email_service()

        recipient_emails = TicketEmailService._build_email_recipients(
            ticket,
            EmailType.REPLY,
            is_admin_reply = is_admin_reply
        )

        if not recipient_emails:
            logger.warning(
                "No recipient emails found for ticket %s reply",
                ticket.id
            )
            return

        try:
            ticket_data = ticket.serialize(include_admin_fields = True)
            message_data = message.serialize(include_admin_fields = True)

            subject, html_body, text_body = TicketEmailTemplates.ticket_reply(
                ticket_data,
                message_data,
                is_admin_reply
            )

            email_service.send_email(
                to_emails = recipient_emails,
                subject = subject,
                html_body = html_body,
                text_body = text_body
            )

        except SQLAlchemyError as e:
            logger.error("Database error sending ticket reply email: %s", e)
        except Exception as e:
            logger.error("Failed to send ticket reply email: %s", e)

    @staticmethod
    def send_player_kicked_email(
        kicked_user_id: int,
        team_name: str,
        event_name: str,
        event_id: int,
        kicked_by_id: int | None = None,
    ) -> None:
        """
        Send email notification when a player is kicked from a team

        Args:
            kicked_user_id: ID of the user who was kicked
            team_name: Name of the team they were kicked from
            event_name: Name of the event
            event_id: ID of the event
            kicked_by_id: ID of the user who kicked them
        """
        email_service = get_email_service()

        kicked_user_email = TicketEmailService._get_user_email(kicked_user_id)

        if not kicked_user_email:
            logger.warning(
                "No email found for kicked user %s",
                kicked_user_id
            )
            return

        try:
            kicked_by_name = None
            if kicked_by_id:
                kicked_by_user = Users.query.get(kicked_by_id)
                if kicked_by_user:
                    kicked_by_name = kicked_by_user.name

            event_url = f"{base_url}/events/{event_id}" if base_url else None

            team_kicked_data: TeamKickedData = {
                'team_name': team_name,
                'event_name': event_name,
                'kicked_by_name': kicked_by_name,
                'event_url': event_url,
            }

            subject, html_body, text_body = TicketEmailTemplates.team_member_kicked(
                team_kicked_data
            )

            email_service.send_email(
                to_emails=[kicked_user_email],
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )

        except SQLAlchemyError as e:
            logger.error("Database error sending player kicked email: %s", e)
        except Exception as e:
            logger.error("Failed to send player kicked email: %s", e)
