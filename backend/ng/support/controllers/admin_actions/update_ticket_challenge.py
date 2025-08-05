"""
Updates ticket's challenge association (admin only).
"""

from ...models.Ticket import Ticket


def update_ticket_challenge(
    challenge_id: int | None,
    ticket: Ticket,
) -> Ticket:
    """
    Update ticket's challenge association
    """
    ticket.update_challenge(
        challenge_id=challenge_id,
        commit=True,
    )

    return ticket
