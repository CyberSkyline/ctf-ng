"""
Ticket event and team association management (admin only).
"""

from ....team.models.Team import Team
from ...models.Ticket import Ticket


def set_ticket_event(
    event_id: int,
    ticket: Ticket,
) -> Ticket:
    """
    Set ticket's event and team association
    """
    team_id = None
    if event_id is not None:
        team = Team.find_by_user_and_event(
            user_id=ticket.author_id,
            event_id=event_id,
        )
        if team:
            team_id = team.id

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
    Remove ticket's event, team, and challenge association.
    """
    ticket.update_event_and_team(
        event_id=None,
        team_id=None,
        commit=False,
    )

    ticket.update_challenge(
        challenge_id=None,
        commit=True,
    )

    return ticket
