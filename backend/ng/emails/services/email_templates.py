"""
Email templates for support ticket notifications using Jinja2
"""

import os
from datetime import datetime
from typing import NotRequired, TypedDict

from flask import current_app
from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
)

from ... import config


class TicketData(TypedDict):
    """
    Type definition for ticket data
    """
    id: int
    subject: str
    status: str
    author_id: int
    opened_timestamp: str
    muted: bool

    author_name: NotRequired[str]
    assigned_to: NotRequired[int | None]
    assigned_to_name: NotRequired[str | None]
    event_id: NotRequired[int | None]
    event_name: NotRequired[str | None]
    team_id: NotRequired[int | None]
    team_name: NotRequired[str | None]
    challenge_id: NotRequired[int | None]
    challenge_name: NotRequired[str | None]
    closed_timestamp: NotRequired[str | None]


class MessageData(TypedDict):
    """
    Type definition for message data
    """
    id: int
    text: str
    author_id: int
    is_admin: bool
    created_at: str

    author_name: NotRequired[str]


class TeamKickedData(TypedDict):
    """
    Type definition for team kicked notification data
    """
    team_name: str
    event_name: str
    kicked_by_name: NotRequired[str | None]
    event_url: NotRequired[str | None]


TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'templates'
)


def format_datetime(value: str) -> str:
    """
    Format ISO datetime string to human-readable format
    """
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M %p UTC')
    except (ValueError, AttributeError):
        return value


jinja_env = Environment(
    loader = FileSystemLoader(TEMPLATE_DIR),
    autoescape = select_autoescape(['html',
                                    'htm']),
    trim_blocks = True,
    lstrip_blocks = True
)

jinja_env.filters['format_datetime'] = format_datetime


class TicketEmailTemplates:
    """
    Templates for ticket notification emails
    """
    @staticmethod
    def _get_base_url() -> str | None:
        """
        Get the base URL for ticket links
        """
        server_domain = current_app.config.get('SERVER_DOMAIN')
        route_prefix = current_app.config.get('ROUTE_PREFIX')
        return f"{server_domain}{route_prefix}"

    @staticmethod
    def new_ticket(ticket_data: TicketData) -> tuple[str, str, str]:
        """
        Generate new ticket notification email

        Args:
            ticket_data: Serialized ticket data

        Returns:
            Tuple of (subject, html_body, text_body)
        """
        base_url = TicketEmailTemplates._get_base_url()
        if not base_url:
            raise ValueError("SERVER_DOMAIN not configured")

        ticket_url = f"{base_url}{config.TICKET_URL_PATH}/{ticket_data['id']}"

        subject = f"New Support Ticket: {ticket_data['subject']}"

        html_template = jinja_env.get_template('new_ticket.html')
        text_template = jinja_env.get_template('new_ticket.txt')

        context = {
            'ticket': ticket_data,
            'ticket_url': ticket_url,
        }

        html_body = html_template.render(context)
        text_body = text_template.render(context)

        return subject, html_body.strip(), text_body.strip()

    @staticmethod
    def ticket_reply(
        ticket_data: TicketData,
        message_data: MessageData,
        is_admin_reply: bool = False
    ) -> tuple[str,
               str,
               str]:
        """
        Generate ticket reply notification

        Args:
            ticket_data: Serialized ticket data
            message_data: Serialized message data
            is_admin_reply: Whether this is an admin reply

        Returns:
            Tuple of (subject, html_body, text_body)
        """
        base_url = TicketEmailTemplates._get_base_url()
        if not base_url:
            raise ValueError("SERVER_DOMAIN not configured")

        ticket_url = f"{base_url}{config.TICKET_URL_PATH}/{ticket_data['id']}"

        reply_type = "Admin" if is_admin_reply else "User"
        subject = f"Support Ticket Reply: {ticket_data['subject']}"

        html_template = jinja_env.get_template('ticket_reply.html')
        text_template = jinja_env.get_template('ticket_reply.txt')

        context = {
            'ticket': ticket_data,
            'message': message_data,
            'ticket_url': ticket_url,
            'reply_type': reply_type,
        }

        html_body = html_template.render(context)
        text_body = text_template.render(context)

        return subject, html_body.strip(), text_body.strip()

    @staticmethod
    def team_member_kicked(
        team_kicked_data: TeamKickedData
    ) -> tuple[str, str, str]:
        """
        Generate team member kicked notification email

        Args:
            team_kicked_data: Data about the kick event

        Returns:
            Tuple of (subject, html_body, text_body)
        """
        subject = f"Removed from Team: {team_kicked_data['team_name']}"

        html_template = jinja_env.get_template('team_member_kicked.html')
        text_template = jinja_env.get_template('team_member_kicked.txt')

        context = {
            'team_name': team_kicked_data['team_name'],
            'event_name': team_kicked_data['event_name'],
            'kicked_by_name': team_kicked_data.get('kicked_by_name'),
            'event_url': team_kicked_data.get('event_url'),
        }

        html_body = html_template.render(context)
        text_body = text_template.render(context)

        return subject, html_body.strip(), text_body.strip()
