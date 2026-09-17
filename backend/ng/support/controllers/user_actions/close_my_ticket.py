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

    # The closing author's own client already mutates its keys
    NotificationService._emit_refetch(
        path=f"/admin/support/tickets/{ticket.id}",
    )

    NotificationService._emit_refetch(
        path="/admin/support/tickets",
    )

    return ticket
