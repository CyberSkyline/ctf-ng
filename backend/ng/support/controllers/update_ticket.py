"""
/backend/ng/support/controllers/update_ticket.py
Updates ticket information with proper authorization.
"""

from typing import Any, Optional

from ...core.utils.logger import get_logger
from ..models.Ticket import Ticket
from ..exceptions import TicketNotFoundError, TicketPermissionError

logger = get_logger(__name__)


def update_ticket(
    ticket_id: int,
    actor_id: int,
    is_admin: bool = False,
    subject: Optional[str] = None,
    event_id: Optional[int] = None,
    team_id: Optional[int] = None,
    challenge_id: Optional[int] = None
) -> dict[str, Any]:
    """Updates ticket information.
    
    Args:
        ticket_id: The ticket to update
        actor_id: User performing the update
        is_admin: Whether the actor is an admin
        subject: New subject (users can update their own)
        event_id: New event association (admin only)
        team_id: New team association (admin only)
        challenge_id: New challenge association (admin only)
        
    Returns:
        dict: Success status and updated ticket data
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
        TicketPermissionError: If user lacks permission
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    # Check permissions TODO
    if not is_admin and ticket.author_id != actor_id:
        raise TicketPermissionError("You do not have permission to update this ticket")
    
    # Track changes for logging
    changes = {}
    
    # Users can only update subject of their own tickets TODO
    if subject is not None and subject != ticket.subject:
        changes["subject"] = {"old": ticket.subject, "new": subject}
    
    # Admin-only updates TODO
    if is_admin:
        if event_id is not None and event_id != ticket.event_id:
            # Validate event exists
            if event_id != 0:  # 0 means unassign from event
                from ...event.models.Event import Event
                if not Event.find_by_id(event_id):
                    raise TicketPermissionError(f"Event with ID {event_id} not found")
            changes["event_id"] = {"old": ticket.event_id, "new": event_id if event_id != 0 else None}
        
        if team_id is not None and team_id != ticket.team_id:
            # Validate team exists
            if team_id != 0:  # 0 means unassign from team
                from ...team.models.Team import Team
                if not Team.find_by_id(team_id):
                    raise TicketPermissionError(f"Team with ID {team_id} not found")
            changes["team_id"] = {"old": ticket.team_id, "new": team_id if team_id != 0 else None}
        
        if challenge_id is not None and challenge_id != ticket.challenge_id:
            changes["challenge_id"] = {"old": ticket.challenge_id, "new": challenge_id if challenge_id != 0 else None}
    
    # Apply updates
    update_data = {}
    if subject is not None:
        update_data["subject"] = subject
    if is_admin:
        if event_id is not None:
            update_data["event_id"] = event_id if event_id != 0 else None
        if team_id is not None:
            update_data["team_id"] = team_id if team_id != 0 else None
        if challenge_id is not None:
            update_data["challenge_id"] = challenge_id if challenge_id != 0 else None
    
    if update_data:
        ticket.update_ticket(**update_data)
        
        logger.info(
            "Ticket updated",
            extra={
                "context": {
                    "ticket_id": ticket_id,
                    "actor_id": actor_id,
                    "is_admin": is_admin,
                    "changes": changes
                }
            }
        )
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=is_admin),
        "changes": changes
    }
