"""
User action controllers for notifications
"""

from .get_notifications import (
    get_unread_count,
    get_my_notifications,
)
from .mark_read import (
    mark_all_read,
    mark_notification_read,
)


__all__ = [
    "mark_all_read",
    "get_unread_count",
    "get_my_notifications",
    "mark_notification_read",
]
