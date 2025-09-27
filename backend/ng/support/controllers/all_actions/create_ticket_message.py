"""
Creates a new message in a support ticket thread.
"""

from ...models.Ticket import Ticket
from ...models.TicketMessage import TicketMessage

from ....notifications.services import NotificationService
from ....notifications.services.notification_service import EmailType


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

    if is_admin and ticket.author_id != author_id:
        NotificationService.notify_ticket_reply(
            ticket_id=ticket.id,
            author_id=author_id,
            recipient_id=ticket.author_id,
            is_admin_reply=True,
        )
    elif not is_admin:
        if ticket.assigned_to:
            NotificationService.notify_ticket_reply(
                ticket_id=ticket.id,
                author_id=author_id,
                recipient_id=ticket.assigned_to,
                is_admin_reply=False,
            )
        else:
            NotificationService._send_ticket_email(
                ticket=ticket,
                email_type=EmailType.REPLY,
                additional_data={
                    'message_data': message.serialize(include_admin_fields=True),
                    'is_admin_reply': False
                }
            )

    return message
