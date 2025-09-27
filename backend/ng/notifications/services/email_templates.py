"""
Email templates for support ticket notifications
"""

from typing import Any
from flask import current_app

from ... import config


# Basic html templates
class TicketEmailTemplates:
    """
    Templates for ticket notification emails
    """
    @staticmethod
    def _get_base_url() -> str | None:
        """
        Get the base URL for ticket links
        """
        domain = current_app.config.get('SERVER_DOMAIN')
        return str(domain) if domain is not None else None

    @staticmethod
    def new_ticket(ticket_data: dict[str, Any]) -> tuple[str, str, str]:
        """
        Generate new ticket notification email
        """
        base_url = TicketEmailTemplates._get_base_url()
        ticket_url = f"{base_url}{config.TICKET_URL_PATH}/{ticket_data['id']}"

        subject = f"New Support Ticket: {ticket_data['subject']}"

        html_body = f"<p>New support ticket #{ticket_data['id']}: {ticket_data['subject']} from {ticket_data.get('author_name', 'Unknown User')}</p>"

        text_body = f"""
New Support Ticket Created

Ticket Details:
- Subject: {ticket_data['subject']}
- Author: {ticket_data.get('author_name', 'Unknown User')}
- Ticket ID: #{ticket_data['id']}
- Created: {ticket_data['opened_timestamp']}
{"- Event: " + ticket_data['event_name'] if ticket_data.get('event_name') else ""}
{"- Team: " + ticket_data['team_name'] if ticket_data.get('team_name') else ""}
{"- Challenge: " + ticket_data['challenge_name'] if ticket_data.get('challenge_name') else ""}

View ticket: {ticket_url}

---
This email was sent by the CTF Support System.
        """

        return subject, html_body.strip(), text_body.strip()

    @staticmethod
    def ticket_reply(
        ticket_data: dict[str,
                          Any],
        message_data: dict[str,
                           Any],
        is_admin_reply: bool = False
    ) -> tuple[str,
               str,
               str]:
        """
        Generate ticket reply notification email

        Returns:
            tuple[subject, html_body, text_body]
        """
        base_url = TicketEmailTemplates._get_base_url()
        ticket_url = f"{base_url}{config.TICKET_URL_PATH}/{ticket_data['id']}"

        reply_type = "Admin" if is_admin_reply else "User"
        subject = f"Support Ticket Reply: {ticket_data['subject']}"

        html_body = f"<p>{reply_type} reply on ticket #{ticket_data['id']}: {message_data['text'][:100]}...</p>"

        text_body = f"""
{reply_type} Reply to Support Ticket

Ticket Details:
- Subject: {ticket_data['subject']}
- Ticket ID: #{ticket_data['id']}
- Status: {ticket_data['status'].title()}

New Message from {message_data.get('author_name', 'Unknown User')}:
{message_data['text']}

Posted at: {message_data['created_at']}

View full conversation: {ticket_url}

---
This email was sent by the CTF Support System.
        """

        return subject, html_body.strip(), text_body.strip()

    @staticmethod
    def ticket_status_change(ticket_data: dict[str,
                                               Any],
                             new_status: str) -> tuple[str,
                                                       str,
                                                       str]:
        """
        Generate ticket status change notification email

        Returns:
            tuple[subject, html_body, text_body]
        """
        base_url = TicketEmailTemplates._get_base_url()
        ticket_url = f"{base_url}{config.TICKET_URL_PATH}/{ticket_data['id']}"

        subject = f"Support Ticket {new_status.title()}: {ticket_data['subject']}"

        html_body = f"<p>Ticket #{ticket_data['id']} status changed to {new_status}</p>"

        text_body = f"""
Support Ticket Status Updated

Status Change:
- New Status: {new_status.title()}

Ticket Details:
- Subject: {ticket_data['subject']}
- Ticket ID: #{ticket_data['id']}
- Author: {ticket_data.get('author_name', 'Unknown User')}

View ticket: {ticket_url}

---
This email was sent by the Support System.
        """

        return subject, html_body.strip(), text_body.strip()

    @staticmethod
    def ticket_assigned(ticket_data: dict[str,
                                          Any],
                        assigned_to_name: str) -> tuple[str,
                                                        str,
                                                        str]:
        """
        Generate ticket assignment notification email

        Returns:
            tuple[subject, html_body, text_body]
        """
        base_url = TicketEmailTemplates._get_base_url()
        ticket_url = f"{base_url}{config.TICKET_URL_PATH}/{ticket_data['id']}"

        subject = f"Support Ticket Assigned: {ticket_data['subject']}"

        html_body = f"<p>Ticket #{ticket_data['id']} assigned to {assigned_to_name}</p>"

        text_body = f"""
Support Ticket Assigned

Assignment Details:
- Assigned to: {assigned_to_name}

Ticket Details:
- Subject: {ticket_data['subject']}
- Ticket ID: #{ticket_data['id']}
- Author: {ticket_data.get('author_name', 'Unknown User')}
- Status: {ticket_data['status'].title()}

View ticket: {ticket_url}

---
This email was sent by the Support System.
        """

        return subject, html_body.strip(), text_body.strip()
