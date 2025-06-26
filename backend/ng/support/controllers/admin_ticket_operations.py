"""
/backend/ng/support/controllers/admin_ticket_operations.py
Admin-only operations for support tickets.
"""

from datetime import datetime
from typing import Any

from CTFd.models import Users

from ...core.utils.logger import get_logger
from ..models.Ticket import Ticket
from ..exceptions import TicketNotFoundError, TicketValidationError

logger = get_logger(__name__)


def assign_ticket(ticket_id: int, user_id: int, admin_id: int) -> dict[str, Any]:
    """Assigns a ticket to a user.
    
    Args:
        ticket_id: The ticket to assign
        user_id: User to assign the ticket to
        admin_id: Admin performing the assignment
        
    Returns:
        dict: Success status and updated ticket data
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
        TicketValidationError: If user doesn't exist
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    # Validate user exists TODO
    user = Users.query.get(user_id)
    if not user:
        raise TicketValidationError(f"User with ID {user_id} not found")
    
    old_assigned_to = ticket.assigned_to
    ticket.assign_to_user(user_id)
    
    logger.info(
        "Ticket assigned",
        extra={
            "context": {
                "ticket_id": ticket_id,
                "assigned_to": user_id,
                "assigned_by": admin_id,
                "previous_assigned_to": old_assigned_to
            }
        }
    )
    
    # Prepare websocket event TODO
    event_data = {
        "type": "ticket_assigned",
        "ticket_id": ticket_id,
        "assigned_to": user_id,
        "assigned_by": admin_id,
        "assigned_user_name": user.name
    }
    # TODO: emit_to_user(user_id, event_data) when websockets implemented
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=True),
        "message": f"Ticket assigned to {user.name}"
    }


def unassign_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Removes assignment from a ticket.
    
    Args:
        ticket_id: The ticket to unassign
        admin_id: Admin performing the operation
        
    Returns:
        dict: Success status and updated ticket data
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    old_assigned_to = ticket.assigned_to
    ticket.unassign()
    
    logger.info(
        "Ticket unassigned",
        extra={
            "context": {
                "ticket_id": ticket_id,
                "unassigned_by": admin_id,
                "previous_assigned_to": old_assigned_to
            }
        }
    )
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=True),
        "message": "Ticket assignment removed"
    }


def close_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Closes a ticket.
    
    Args:
        ticket_id: The ticket to close
        admin_id: Admin performing the operation
        
    Returns:
        dict: Success status and updated ticket data
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    if ticket.status == "closed":
        raise TicketValidationError("Ticket is already closed")
    
    ticket.close_ticket()
    
    logger.info(
        "Ticket closed",
        extra={
            "context": {
                "ticket_id": ticket_id,
                "closed_by": admin_id
            }
        }
    )
    
    # Prepare websocket event TODO
    event_data = {
        "type": "ticket_closed",
        "ticket_id": ticket_id,
        "closed_by": admin_id
    }
    # TODO: emit_to_user(ticket.author_id, event_data) when websockets implemented
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=True),
        "message": "Ticket closed successfully"
    }


def reopen_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Reopens a closed ticket.
    
    Args:
        ticket_id: The ticket to reopen
        admin_id: Admin performing the operation
        
    Returns:
        dict: Success status and updated ticket data
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    if ticket.status != "closed":
        raise TicketValidationError("Ticket is not closed")
    
    ticket.reopen_ticket()
    
    logger.info(
        "Ticket reopened",
        extra={
            "context": {
                "ticket_id": ticket_id,
                "reopened_by": admin_id
            }
        }
    )
    
    # Prepare websocket event TODO
    event_data = {
        "type": "ticket_reopened",
        "ticket_id": ticket_id,
        "reopened_by": admin_id
    }
    # TODO: emit_to_user(ticket.author_id, event_data) when websockets implemented
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=True),
        "message": "Ticket reopened successfully"
    }


def mute_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Mutes a ticket.
    
    Args:
        ticket_id: The ticket to mute
        admin_id: Admin performing the operation
        
    Returns:
        dict: Success status and updated ticket data
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    if ticket.muted:
        raise TicketValidationError("Ticket is already muted")
    
    ticket.mute_ticket()
    
    logger.info(
        "Ticket muted",
        extra={
            "context": {
                "ticket_id": ticket_id,
                "muted_by": admin_id
            }
        }
    )
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=True),
        "message": "Ticket muted successfully"
    }


def unmute_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Unmutes a ticket.
    
    Args:
        ticket_id: The ticket to unmute
        admin_id: Admin performing the operation
        
    Returns:
        dict: Success status and updated ticket data
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    if not ticket.muted:
        raise TicketValidationError("Ticket is not muted")
    
    ticket.unmute_ticket()
    
    logger.info(
        "Ticket unmuted",
        extra={
            "context": {
                "ticket_id": ticket_id,
                "unmuted_by": admin_id
            }
        }
    )
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=True),
        "message": "Ticket unmuted successfully"
    }


def get_ticket_statistics() -> dict[str, Any]:
    """Gets overall ticket statistics for admin dashboard.
    
    Returns:
        dict: Ticket statistics
    """
    stats = Ticket.get_ticket_stats()
    
    # Add average response time calculation
    from ..models.Ticket import Ticket as TicketModel
    
    # Get tickets with first admin response TODO
    tickets_with_response = TicketModel.query.filter(
        TicketModel.first_admin_response_timestamp.isnot(None)
    ).all()
    
    if tickets_with_response:
        total_response_time = sum(
            (ticket.first_admin_response_timestamp - ticket.opened_timestamp).total_seconds()
            for ticket in tickets_with_response
        )
        avg_response_time_seconds = total_response_time / len(tickets_with_response)
        avg_response_time_hours = avg_response_time_seconds / 3600
        stats["avg_response_time_hours"] = round(avg_response_time_hours, 2)
    else:
        stats["avg_response_time_hours"] = None
    
    # Get tickets closed today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tickets_closed_today = TicketModel.query.filter(
        TicketModel.closed_timestamp >= today_start
    ).count()
    stats["closed_today"] = tickets_closed_today
    
    return {
        "success": True,
        "statistics": stats
    }
