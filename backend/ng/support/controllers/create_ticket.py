"""
/backend/ng/support/controllers/create_ticket.py
Creates a new support ticket.
"""

from typing import Any, Optional

from ...core.utils.logger import get_logger
from ..models.Ticket import Ticket
from ..models.TicketTag import TicketTag
from ..exceptions import TicketValidationError, TagNotFoundError

logger = get_logger(__name__)


def create_ticket(
    subject: str,
    author_id: int,
    event_id: Optional[int] = None,
    team_id: Optional[int] = None,
    challenge_id: Optional[int] = None,
    tag_ids: Optional[list[int]] = None
) -> dict[str, Any]:
    """Creates a new support ticket.
    
    Args:
        subject: Ticket subject line
        author_id: User ID creating the ticket
        event_id: Optional event association
        team_id: Optional team association  
        challenge_id: Optional challenge association
        tag_ids: Optional list of tag IDs to attach
        
    Returns:
        dict: Success status and created ticket data
        
    Raises:
        TicketValidationError: If validation fails
        TagNotFoundError: If specified tags don't exist
    """
    # Validate tags exist if provided TODO
    tags = []
    if tag_ids:
        for tag_id in tag_ids:
            tag = TicketTag.find_by_id(tag_id)
            if not tag:
                raise TagNotFoundError(f"Tag with ID {tag_id} not found")
            tags.append(tag)
    
    # Validate associations exist if provided TODO
    if event_id:
        from ...event.models.Event import Event
        event = Event.find_by_id(event_id)
        if not event:
            raise TicketValidationError(f"Event with ID {event_id} not found")
    
    if team_id:
        from ...team.models.Team import Team
        team = Team.find_by_id(team_id)
        if not team:
            raise TicketValidationError(f"Team with ID {team_id} not found")
    
    # Create the ticket
    ticket = Ticket.create(
        subject=subject,
        author_id=author_id,
        event_id=event_id,
        team_id=team_id,
        challenge_id=challenge_id,
        tags=tags
    )
    
    logger.info(
        "Support ticket created",
        extra={
            "context": {
                "ticket_id": ticket.id,
                "author_id": author_id,
                "subject": subject[:50] + "..." if len(subject) > 50 else subject,
                "event_id": event_id,
                "team_id": team_id
            }
        }
    )
    
    # Prepare websocket event data for future implementation TODO
    event_data = {
        "type": "ticket_created",
        "ticket_id": ticket.id,
        "ticket": ticket.serialize(),
        "author_id": author_id
    }
    # TODO: emit_to_admins(event_data) when websockets implemented
    
    return {
        "success": True,
        "ticket": ticket.serialize(),
        "message": "Ticket created successfully"
    }
