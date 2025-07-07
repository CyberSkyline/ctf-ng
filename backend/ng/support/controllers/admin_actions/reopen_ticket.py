"""
Reopens a previously closed ticket
"""

from flask import g

from ....core import ValidationError
from ....core.utils import emit_event


def reopen_ticket(ticket_id: int, admin_id: int):
    """Reopens a previously closed ticket."""
    ticket = g.ticket

    if ticket.status != "closed":
        raise ValidationError("Ticket is not closed")

    ticket.reopen_ticket()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

