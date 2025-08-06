"""
Ticket challenge association management (admin only).
"""

from ...models.Ticket import Ticket


def set_ticket_challenge(
    challenge_id: int,
    ticket: Ticket,
) -> Ticket:
    """
    Set ticket's challenge association
    """
    ticket.update_challenge(
        challenge_id=challenge_id,
        commit=True,
    )

    return ticket


def remove_ticket_challenge(
    ticket: Ticket,
) -> Ticket:
    """
    Remove ticket's challenge association
    """
    ticket.update_challenge(
        challenge_id=None,
        commit=True,
    )

    return ticket