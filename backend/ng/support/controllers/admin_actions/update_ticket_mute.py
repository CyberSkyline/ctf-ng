"""
Toggles ticket mute status (admin only).
"""

from ...models.Ticket import Ticket


def update_ticket_mute(
    ticket_id: int,
    muted: bool,
    ticket=None,
) -> Ticket:
    """
    Toggle ticket mute status.
    """
    ticket.toggle_mute(muted=muted, commit=True)

    return ticket
