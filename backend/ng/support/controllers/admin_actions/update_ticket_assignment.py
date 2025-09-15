"""
Ticket assignment management (admin only).
"""

from ...models.Ticket import Ticket
from ....user.models.User import User
from ....notifications.services import NotificationService


def assign_ticket(
    user: User,
    ticket: Ticket,
) -> Ticket:
    """
    Assign a ticket to a user
    """
    ticket.assign_to_user(user_id=user.id, commit=True)

    NotificationService.notify_ticket_assigned(
        ticket_id=ticket.id,
        assigned_to_id=user.id,
        assigned_by_id=user.id,
    )

    return ticket


def unassign_ticket(
    ticket: Ticket,
) -> Ticket:
    """
    Remove ticket assignment
    """
    ticket.unassign(commit=True)

    return ticket
