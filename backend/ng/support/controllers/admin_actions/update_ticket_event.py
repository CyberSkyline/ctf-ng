"""
Updates ticket's event and team association (admin only).
"""

from ...models.Ticket import Ticket


def update_ticket_event(
    ticket_id: int,
    event_id: int | None,
    team_id: int | None,
    ticket=None,
) -> Ticket:
    """
    Update ticket's event and team association.
    """
    ticket.update_event_and_team(
        event_id=event_id,
        team_id=team_id,
        commit=True,
    )

    return ticket
