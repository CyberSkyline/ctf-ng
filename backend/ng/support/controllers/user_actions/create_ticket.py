"""
Creates a new support ticket with initial message.
"""

from CTFd.models import db

from ....core.exceptions import NotFoundError
from ....user.models.User import User
from ....team.models.Team import Team
from ...models.Ticket import Ticket
from ...models.TicketMessage import TicketMessage
from ....notifications.services import NotificationService
from ....emails.services import TicketEmailService


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

    try:
        # Create ticket without committing
        ticket = Ticket.create_ticket(
            subject=subject,
            author_id=current_user.id,
            event_id=event_id,
            team_id=team_id,
            challenge_id=challenge_id,
            commit=False,
        )

        # Flush to assign ticket ID
        db.session.flush()

        # Create initial message without committing
        TicketMessage.create_message(
            text=text,
            ticket_id=ticket.id,
            author_id=current_user.id,
            commit=False,
        )

        # Commit both together
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    NotificationService.notify_new_ticket(
        ticket_id=ticket.id,
        author_id=current_user.id,
        subject=subject,
    )

    TicketEmailService.send_new_ticket_email(ticket=ticket)

    return ticket
