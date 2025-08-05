"""
Updates ticket assignment (admin only).
"""

from ...models.Ticket import Ticket
from ....user.models.User import User


def update_ticket_assignment(
    user: User | None,
    ticket: Ticket,
) -> Ticket:
    """
    Assign or unassign a ticket
    """
    if user is None:
        ticket.unassign(commit=True)
    else:
        ticket.assign_to_user(user_id=user.id, commit=True)

    return ticket
