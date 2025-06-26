"""
/backend/ng/support/controllers/create_ticket_message.py
Creates a new message in a support ticket thread.
"""

from typing import Any
from datetime import datetime

from CTFd.models import db

from ...core.utils.logger import get_logger
from ..models.Ticket import Ticket
from ..models.TicketMessage import TicketMessage
from ..exceptions import TicketNotFoundError, TicketPermissionError, TicketOperationError

logger = get_logger(__name__)


def create_ticket_message(
    ticket_id: int,
    text: str,
    author_id: int,
    is_admin: bool = False
) -> dict[str, Any]:
    """Creates a new message in a ticket thread.
    
    Args:
        ticket_id: The ticket to add message to
        text: Message content (markdown supported)
        author_id: User ID of the message author
        is_admin: Whether the author is an admin
        
    Returns:
        dict: Success status and created message data
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
        TicketPermissionError: If user lacks permission
        TicketOperationError: If ticket is closed and user is not admin
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    # Check permissions - non-admins can only reply to their own tickets TODO
    if not is_admin and ticket.author_id != author_id:
        raise TicketPermissionError("You do not have permission to reply to this ticket")
    
    # Check if ticket is closed - only admins can reply to closed tickets TODO
    if ticket.status == "closed" and not is_admin:
        raise TicketOperationError("Cannot reply to a closed ticket")
    
    # If ticket was closed and admin is replying, reopen it TODO
    if ticket.status == "closed" and is_admin:
        ticket.reopen_ticket(commit=False)
        logger.info(
            "Ticket reopened by admin reply",
            extra={
                "context": {
                    "ticket_id": ticket_id,
                    "admin_id": author_id
                }
            }
        )
    
    # Create the message
    message = TicketMessage.create(
        text=text,
        ticket_id=ticket_id,
        author_id=author_id,
        commit=False
    )
    
    # Update ticket's last_updated timestamp
    ticket.last_updated = datetime.utcnow()
    
    # If this is the first admin response, record it
    if is_admin and ticket.first_admin_response_timestamp is None:
        ticket.set_first_admin_response(commit=False)
    
    # Commit all changes together
    db.session.commit()
    
    # Prepare websocket event data TODO
    event_data = {
        "type": "ticket_message",
        "ticket_id": ticket_id,
        "message": message.serialize(),
        "author_id": author_id,
        "is_admin": is_admin
    }
    # TODO: emit_to_ticket_subscribers(event_data) when websockets implemented
    
    return {
        "success": True,
        "message": message.serialize(),
        "ticket_reopened": ticket.status == "open" and ticket.closed_timestamp is None
    }
