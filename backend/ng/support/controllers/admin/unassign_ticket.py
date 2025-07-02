"""
Removes the assignment from a ticket
"""

from flask import g
from typing import Any

from ....core.utils import emit_event


def unassign_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Removes the assignment from a ticket."""
    ticket = g.ticket
    ticket.unassign()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "assignment_removed": True,
    }
