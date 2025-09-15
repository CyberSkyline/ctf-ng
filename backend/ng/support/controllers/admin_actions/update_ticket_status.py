"""
Toggles ticket open/closed status (admin only).
"""

from ....user.models.User import User
from ...models.Ticket import Ticket
from ....notifications.services import NotificationService


def update_ticket_status(
    closed: bool,
    ticket: Ticket,
    current_user: User,
) -> Ticket:
    """
    Toggle ticket open/closed status
    """
    if closed:
        ticket.close_ticket(commit=True)
        status = "closed"
    else:
        ticket.reopen_ticket(commit=True)
        status = "reopened"

    # Notify ticket author about status change
    NotificationService.notify_ticket_status_change(
        ticket_id=ticket.id,
        recipient_id=ticket.author_id,
        new_status=status,
        changed_by_id=current_user.id,
    )

    return ticket
