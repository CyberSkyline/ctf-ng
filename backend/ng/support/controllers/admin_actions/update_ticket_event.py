"""
Ticket event and team association management (admin only).
"""

from ...models.Ticket import Ticket


def set_ticket_event(
    event_id: int,
    team_id: int,
    ticket: Ticket,
) -> Ticket:
    """
    Set ticket's event and team association
    """
    ticket.update_event_and_team(
        event_id=event_id,
        team_id=team_id,
        commit=True,
    )

    return ticket


def remove_ticket_event(
    ticket: Ticket,
) -> Ticket:
    """
    Remove ticket's event and team association
    """
    ticket.update_event_and_team(
        event_id=None,
        team_id=None,
        commit=True,
    )

    return ticket