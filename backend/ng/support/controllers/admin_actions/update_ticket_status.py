"""
Toggles ticket open/closed status (admin only).
"""

from ....core.utils import emit_event
from ...models.Ticket import Ticket


def update_ticket_status(
    closed: bool,
    ticket: Ticket,
    current_user,
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
        data={"ticket_id": ticket.id, "changed_by": current_user.id},
        room=f"ticket_{ticket.id}",
    )

    return ticket
