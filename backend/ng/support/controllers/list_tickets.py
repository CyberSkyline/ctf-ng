"""
/backend/ng/support/controllers/list_tickets.py
Lists support tickets with optional filtering.
"""

from typing import Any, Optional

from ..models.Ticket import Ticket


def list_tickets(
    user_id: Optional[int] = None,
    status: str = "all",
    assigned_to: Optional[int] = None,
    event_id: Optional[int] = None,
    team_id: Optional[int] = None,
    is_admin: bool = False
) -> dict[str, Any]:
    """Lists support tickets based on filters and permissions.
    
    Args:
        user_id: Filter by ticket author (for non-admin users, this is enforced)
        status: Filter by status (open, closed, muted, all)
        assigned_to: Filter by assigned user ID (admin only)
        event_id: Filter by event ID
        team_id: Filter by team ID
        is_admin: Whether the requesting user is an admin
        
    Returns:
        dict: Success status and list of tickets
    """
    # Start with base query
    query = Ticket.query
    
    # Non-admins can only see their own tickets TODO
    if not is_admin and user_id:
        query = query.filter_by(author_id=user_id)
    elif user_id and is_admin:
        # Admin filtering by specific user
        query = query.filter_by(author_id=user_id)
    
    # Status filtering
    if status == "open":
        query = query.filter(
            Ticket.closed_timestamp.is_(None),
            Ticket.muted.is_(False)
        )
    elif status == "closed":
        query = query.filter(Ticket.closed_timestamp.isnot(None))
    elif status == "muted":
        query = query.filter(Ticket.muted.is_(True))
    
    # Additional filters (admin only)
    if is_admin:
        if assigned_to is not None:
            query = query.filter_by(assigned_to=assigned_to)
        if event_id is not None:
            query = query.filter_by(event_id=event_id)
        if team_id is not None:
            query = query.filter_by(team_id=team_id)
    
    # Order by last updated descending TODO
    tickets = query.order_by(Ticket.last_updated.desc()).all()
    
    # Serialize tickets with appropriate fields TODO
    serialized_tickets = [
        ticket.serialize(include_admin_fields=is_admin) 
        for ticket in tickets
    ]
    
    return {
        "success": True,
        "tickets": serialized_tickets,
        "total": len(tickets),
        "filters": {
            "status": status,
            "user_id": user_id,
            "assigned_to": assigned_to if is_admin else None,
            "event_id": event_id if is_admin else None,
            "team_id": team_id if is_admin else None
        }
    }
