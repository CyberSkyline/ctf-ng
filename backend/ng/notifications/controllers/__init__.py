"""
Notification controllers package
"""

from .user_actions import (
    mark_all_read,
    get_unread_count,
    get_my_notifications,
    mark_notification_read,
)
from .admin_actions import (
    send_announcement,
    get_all_announcements,
    send_event_announcement,
)
from .all_actions import (
    get_active_announcements,
)


__all__ = [
    "mark_all_read",
    "get_unread_count",
    "send_announcement",
    "get_my_notifications",
    "get_all_announcements",
    "mark_notification_read",
    "send_event_announcement",
    "get_active_announcements",
]
