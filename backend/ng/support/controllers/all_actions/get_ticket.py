"""
Gets ticket details with all messages for display.
"""

from typing import Any


def get_ticket(ticket_id: int, ticket=None) -> dict[str, Any]:
    """
    Get ticket details with all messages.
    """
    messages = ticket.get_messages()

    return {"ticket": ticket, "messages": messages}
