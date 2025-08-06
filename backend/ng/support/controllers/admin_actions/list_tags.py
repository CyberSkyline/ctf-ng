"""
Lists all ticket tags (admin only).
"""

from ...models.TicketTag import TicketTag


def list_tags() -> list[TicketTag]:
    """
    Get all ticket tags
    """
    return TicketTag.get_all_tags()
