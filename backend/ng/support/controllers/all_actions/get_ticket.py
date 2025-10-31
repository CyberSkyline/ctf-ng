"""
Gets ticket details with all messages for display.
"""

from typing import Any

from ...models.Ticket import Ticket
from ...models.TicketAttachment import TicketAttachment


def get_ticket(ticket: Ticket) -> dict[str, Any]:
    """
    Get ticket details with all messages and attachments
    """
    messages = ticket.get_messages()
    attachments = TicketAttachment.find_by_ticket(ticket.id)

    return {
        "ticket": ticket,
        "messages": messages,
        "attachments": attachments
    }
