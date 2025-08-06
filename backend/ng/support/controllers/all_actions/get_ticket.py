"""
Gets ticket details with all messages for display.
"""

from typing import Any

from ...models.Ticket import Ticket


def get_ticket(ticket: Ticket) -> dict[str, Any]:
    """
    Get ticket details with all messages.
    """
    messages = ticket.get_messages()

    return {"ticket": ticket, "messages": messages}
