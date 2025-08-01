"""
Toggles ticket open/closed status (admin only).
"""

from ....core.utils import emit_event
from ...models.Ticket import Ticket


def update_ticket_status(
    ticket_id: int,
    closed: bool,
    ticket=None,
    current_user=None,
) -> Ticket:
    """
    Toggle ticket open/closed status
    """
    if closed:
        ticket.close_ticket(commit=True)
        event_name = "ticket_closed"
    else:
        ticket.reopen_ticket(commit=True)
        event_name = "ticket_reopened"

    # TODO: Refactor in near future with notifications implemenation
    emit_event(
        event_name=event_name,
        data={"ticket_id": ticket_id, "changed_by": current_user.id},
        room=f"ticket_{ticket_id}",
    )

    return ticket
