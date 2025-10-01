"""
Get active announcements
"""

from ..models import Announcement


def get_active_announcements(
    event_id: int | None = None,
) -> list[Announcement]:
    """
    Get active announcements for display
    """
    return Announcement.get_active_announcements(
        event_id = event_id,
    )
