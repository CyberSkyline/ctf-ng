"""
Changes a ticket's status to 'closed'
"""

from flask import g
from typing import Any

from ....core import ValidationError
from ....core.utils import emit_event


def close_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Changes a ticket's status to 'closed'."""
    ticket = g.ticket

    if ticket.status == "closed":
        raise ValidationError("Ticket is already closed")

    ticket.close_ticket()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "ticket_closed": True,
    }
