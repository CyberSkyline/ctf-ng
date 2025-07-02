"""
Changes a ticket's status to 'muted'
"""

from flask import g
from typing import Any

from ....core import ValidationError
from ....core.utils import emit_event


def mute_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Changes a ticket's status to 'muted'."""
    ticket = g.ticket

    if ticket.muted:
        raise ValidationError("Ticket is already muted")

    ticket.mute_ticket()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "ticket_muted": True,
    }
