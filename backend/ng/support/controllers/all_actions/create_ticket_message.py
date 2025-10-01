"""
Creates a new message in a support ticket thread.
"""

from ...models.Ticket import Ticket
from ...models.TicketMessage import TicketMessage

from ....notifications.services import NotificationService
from ....emails.services import TicketEmailService


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

    # Implicit assignment: admin replies = admin takes ownership
    if is_admin and not ticket.assigned_to:
        ticket.assign_to_user(author_id, commit=True)

    messages = ticket.get_messages()
    message = messages[-1]

    # Handle DB notifications + WebSocket events
    NotificationService.handle_ticket_message_notifications(
        ticket=ticket,
        message=message,
        author_id=author_id,
        is_admin=is_admin,
    )

    # Handle email notifications (separate service)
    if not ticket.muted:
        TicketEmailService.send_ticket_reply_email(
            ticket=ticket,
            message=message,
            is_admin_reply=is_admin
        )

    return message