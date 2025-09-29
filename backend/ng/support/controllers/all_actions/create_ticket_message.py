"""
Creates a new message in a support ticket thread.
"""

from ...models.Ticket import Ticket
from ...models.TicketMessage import TicketMessage
from ....notifications.services import NotificationService


def create_ticket_message(
    text: str,
    author_id: int,
    ticket: Ticket,
    is_admin: bool = False,
) -> TicketMessage:
    """
    Creates a new message in a ticket thread.
    """
    if ticket.status == "closed" and is_admin:
        ticket.reopen_ticket(commit=False)

    ticket.add_message(
        text=text,
        author_id=author_id,
        is_admin=is_admin,
        commit=True,
    )

    messages = ticket.get_messages()
    message = messages[-1]

    if is_admin:
        # Admin replying to user's ticket
        if ticket.author_id != author_id:
            # Notify the ticket author (user)
            NotificationService.notify_ticket_reply(
                ticket_id=ticket.id,
                author_id=author_id,
                recipient_id=ticket.author_id,
                is_admin_reply=True,
            )
    else:
        # User replying to ticket
        if ticket.assigned_to:
            # Ticket is assigned - notify only the assigned admin
            NotificationService.notify_ticket_reply(
                ticket_id=ticket.id,
                author_id=author_id,
                recipient_id=ticket.assigned_to,
                is_admin_reply=False,
            )
        else:
            # Ticket is unassigned - notify all support staff
            NotificationService.notify_unassigned_ticket_reply(
                ticket_id=ticket.id,
                author_id=author_id,
            )

    return message
