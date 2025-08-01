"""
Allows users to close their own support tickets.
"""

from ....core.utils import emit_event
from ...models.Ticket import Ticket


def close_my_ticket(
    ticket_id: int,
    ticket=None,
    current_user=None,
) -> Ticket:
    """
    Close user's own ticket.
    """
    ticket.close_ticket(commit=True)

    # TODO: Refactor in near future with notifications implemenation
    emit_event(
        event_name="ticket_closed",
        data={"ticket_id": ticket_id, "closed_by": current_user.id},
        room=f"ticket_{ticket_id}",
    )

    return ticket
