"""
Creates a new message in a support ticket thread.
"""

from flask import g
from typing import Any

from ...core.validation import validate_ticket_reply_allowed
from ...core.utils import emit_event


def create_ticket_message(ticket_id: int, text: str, author_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Creates a new message in a ticket thread."""
    ticket = g.ticket

    validate_ticket_reply_allowed(ticket, is_admin)

    result = ticket.add_message_with_updates(text=text, author_id=author_id, is_admin=is_admin)

    emit_event(
        event_name="new_message",
        data=result["message"].serialize(),
        room=f"ticket_{ticket_id}",
    )

    return {
        "message": result["message"],
        "ticket_reopened": result["ticket_reopened"],
    }
