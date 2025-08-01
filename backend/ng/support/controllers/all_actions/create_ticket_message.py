"""
Creates a new message in a support ticket thread.
"""

from ....core.utils import emit_event
from ...models.TicketMessage import TicketMessage


def create_ticket_message(
    ticket_id: int,
    text: str,
    author_id: int,
    is_admin: bool = False,
    ticket=None,
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

    # TODO: Refactor in near future with notifications implemenation
    emit_event(
        event_name="new_message",
        data={"ticket_id": ticket_id, "message": message.serialize()},
        room=f"ticket_{ticket_id}",
    )

    return message
