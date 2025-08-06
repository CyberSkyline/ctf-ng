"""
Ticket assignment management (admin only).
"""

from ...models.Ticket import Ticket
from ....user.models.User import User


def assign_ticket(
    user: User,
    ticket: Ticket,
) -> Ticket:
    """
    Assign a ticket to a user
    """
    ticket.assign_to_user(user_id=user.id, commit=True)

    return ticket


def unassign_ticket(
    ticket: Ticket,
) -> Ticket:
    """
    Remove ticket assignment
    """
    ticket.unassign(commit=True)

    return ticket