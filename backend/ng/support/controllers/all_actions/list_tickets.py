"""
Lists support tickets with optional filtering based on user permissions.
"""

from ...models.Ticket import Ticket

def list_tickets(
    user_id: int | None = None,
    status: str = "all",
    assigned_to: int | None = None,
    event_id: int | None = None,
    team_id: int | None = None,
    is_admin: bool = False,
) -> list[Ticket]:
    """Lists support tickets based on filters and user permissions."""
    tickets = Ticket.find_filtered_tickets(
        user_id=user_id,
        status=status,
        assigned_to=assigned_to,
        event_id=event_id,
        team_id=team_id,
        is_admin=is_admin,
    )

    return tickets
