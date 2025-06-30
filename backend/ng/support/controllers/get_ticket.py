"""
Retrieves detailed information about a specific ticket, including all messages.
"""

from flask import g
from typing import Any

from CTFd.models import Users

from ..models.TicketMessage import TicketMessage


def get_ticket(ticket_id: int, user_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Gets detailed information for a single ticket, including its full message history."""
    ticket = g.ticket
    messages = TicketMessage.find_by_ticket(ticket_id)

    author_info: dict[str, str] = {}
    if is_admin and ticket.author_id:
        author = Users.query.get(ticket.author_id)
        if author:
            author_info = {"author_name": author.name, "author_email": author.email}

    return {"ticket": ticket, "messages": messages, **author_info}
