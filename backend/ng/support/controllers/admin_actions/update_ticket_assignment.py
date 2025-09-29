"""
Ticket assignment management (admin only).
"""

from ...models.Ticket import Ticket
from ....user.models.User import User
from ....notifications.services import NotificationService
from ....permissions.controllers import get_support_role_users
from ....core.exceptions import ValidationError


def assign_ticket(
    user: User,
    ticket: Ticket,
) -> Ticket:
    """
    Assign a ticket to a user (must have ADMIN or SUPPORT role)
    """
    # Validate user has support role
    support_users = get_support_role_users()
    support_user_ids = [su.ctfd_user.id for su in support_users]

    if user.id not in support_user_ids:
        raise ValidationError(
            "Tickets can only be assigned to users with ADMIN or SUPPORT roles"
        )

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
