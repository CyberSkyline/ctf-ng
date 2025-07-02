"""
Removes the 'muted' status from a ticket
"""

from flask import g
from typing import Any

from ....core import ValidationError
from ....core.utils import emit_event


def unmute_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Removes the 'muted' status from a ticket."""
    ticket = g.ticket

    if not ticket.muted:
        raise ValidationError("Ticket is not muted")

    ticket.unmute_ticket()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "ticket_unmuted": True,
    }
