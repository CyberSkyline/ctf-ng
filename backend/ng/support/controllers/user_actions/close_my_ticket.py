"""
Allows users to close their own support tickets.
"""

from ....core.utils import emit_event
from ...models.Ticket import Ticket


def close_my_ticket(
    ticket: Ticket,
    current_user,
) -> Ticket:
    """
    Close user's own ticket.
    """
    ticket.close_ticket(commit=True)

    # TODO: Refactor in near future with notifications implemenation
    emit_event(
        event_name="ticket_closed",
        data={"ticket_id": ticket.id, "closed_by": current_user.id},
        room=f"ticket_{ticket.id}",
    )

    return ticket
