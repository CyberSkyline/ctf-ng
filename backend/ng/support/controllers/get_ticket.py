"""
/backend/ng/support/controllers/get_ticket.py
Retrieves detailed information about a specific ticket.
"""

from typing import Any

from ..models.Ticket import Ticket
from ..models.TicketMessage import TicketMessage
from ..exceptions import TicketNotFoundError, TicketPermissionError


def get_ticket(ticket_id: int, user_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Gets detailed information about a specific ticket.
    
    Args:
        ticket_id: The ticket ID to retrieve
        user_id: The requesting user's ID
        is_admin: Whether the requesting user is an admin
        
    Returns:
        dict: Success status and ticket details with messages
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
        TicketPermissionError: If user lacks permission to view ticket
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    # Check permissions - non-admins can only view their own tickets TODO
    if not is_admin and ticket.author_id != user_id:
        raise TicketPermissionError("You do not have permission to view this ticket")
    
    # Get all messages for the ticket
    messages = TicketMessage.find_by_ticket(ticket_id)
    
    # Serialize ticket and messages TODO
    ticket_data = ticket.serialize(include_admin_fields=is_admin)
    ticket_data["messages"] = [msg.serialize() for msg in messages]
    
    # Add additional context for admins TODO
    if is_admin and ticket.author_id:
        from CTFd.models import Users
        author = Users.query.get(ticket.author_id)
        if author:
            ticket_data["author_name"] = author.name
            ticket_data["author_email"] = author.email
    
    return {
        "success": True,
        "ticket": ticket_data
    }
