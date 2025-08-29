"""
Allows users to close their own support tickets.
"""

from ....user.models.User import User
from ...models.Ticket import Ticket

from ....notifications.services import NotificationService


def close_my_ticket(
    ticket: Ticket,
    current_user: User,
) -> Ticket:
    """
    Close user's own ticket.
    """
    ticket.close_ticket(commit=True)

    NotificationService._emit_refetch(
        path=f"/ng/support/tickets/{ticket.id}",
        room=f"ticket_{ticket.id}"
    )

    return ticket
