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

    user_ids = [ticket.author_id]
    if ticket.assigned_to and ticket.assigned_to != ticket.author_id:
        user_ids.append(ticket.assigned_to)

    NotificationService._emit_refetch(
        path=f"/ng/support/tickets/{ticket.id}",
        user_ids=user_ids
    )

    return ticket
