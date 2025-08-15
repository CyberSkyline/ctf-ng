"""
Creates a new support ticket with initial message.
"""

from ....core.utils import emit_event
from ....user.models.User import User
from ...models.Ticket import Ticket

def create_ticket(
    subject: str,
    text: str,
    current_user: User,
    event_id: int | None = None,
    team_id: int | None = None,
    challenge_id: int | None = None,
) -> Ticket:
    """
    Create a new support ticket with initial message
    """
    ticket = Ticket.create_ticket(
        subject=subject,
        author_id=current_user.id,
        event_id=event_id,
        team_id=team_id,
        challenge_id=challenge_id,
        commit=True,
    )

    ticket.add_message(
        text=text,
        author_id=current_user.id,
        is_admin=False,
        commit=True,
    )

    # TODO: Refactor in near future with notifications implemenation
    emit_event(
        event_name="new_ticket",
        data={"ticket": ticket.serialize()},
        room="support_admin",
    )

    return ticket
