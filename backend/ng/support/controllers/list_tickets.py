"""
Lists support tickets with optional filtering based on user permissions.
"""

from typing import Any

from ..models.Ticket import Ticket


def list_tickets(
    user_id: int | None = None,
    status: str = "all",
    assigned_to: int | None = None,
    event_id: int | None = None,
    team_id: int | None = None,
    is_admin: bool = False,
) -> dict[str, Any]:
    """Lists support tickets based on filters and user permissions."""
    tickets = Ticket.find_filtered_tickets(
        user_id=user_id,
        status=status,
        assigned_to=assigned_to,
        event_id=event_id,
        team_id=team_id,
        is_admin=is_admin,
    )

    return {
        "tickets": tickets,
        "total": len(tickets),
        "filters": {
            "status": status,
            "user_id": user_id,
            "assigned_to": assigned_to if is_admin else None,
            "event_id": event_id if is_admin else None,
            "team_id": team_id if is_admin else None,
        },
    }
