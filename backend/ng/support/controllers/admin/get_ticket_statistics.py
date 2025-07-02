"""
Gets overall ticket statistics for the admin dashboard
"""

from typing import Any

from ...models.Ticket import Ticket


def get_ticket_statistics() -> dict[str, Any]:
    """Gets overall ticket statistics for the admin dashboard."""
    stats = Ticket.get_ticket_stats()
    return {"statistics": stats}
