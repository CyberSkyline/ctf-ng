"""
Creates a new support ticket with initial message.
"""

from ....core.exceptions import NotFoundError
from ....user.models.User import User
from ....team.models.Team import Team
from ...models.Ticket import Ticket
from ....notifications.services import NotificationService

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
    if event_id is not None and team_id is None:
        team = Team.find_by_user_and_event(user_id=current_user.id, event_id=event_id)
        if not team:
            raise NotFoundError(f"User not found in any team for event {event_id}")
        team_id = team.id

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

    NotificationService.notify_new_ticket(
        ticket_id=ticket.id,
        author_id=current_user.id,
        subject=subject,
    )

    return ticket
