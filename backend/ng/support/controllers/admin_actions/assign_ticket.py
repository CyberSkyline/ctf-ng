"""
Assigns a ticket to a support user.
"""

from flask import g

from ....core import ValidationError
from ....core.utils import emit_event


def assign_ticket(ticket_id: int, user_id: int, admin_id: int):
    """Assigns a ticket to a support user."""
    ticket = g.ticket

    result = ticket.assign_to_user_with_validation(user_id)
    if not result["success"]:
        raise ValidationError(result["error"])

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )
