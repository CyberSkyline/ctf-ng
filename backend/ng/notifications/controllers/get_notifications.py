"""
Get notifications for users
"""

from ..models import Notification


def get_my_notifications(
    user_id: int,
    is_read: bool | None = None,
) -> list[Notification]:
    """
    Get notifications for a user with optional filters
    """
    return Notification.find_filtered_notifications(
        recipient_id = user_id,
        is_read = is_read,
    )


def get_unread_count(user_id: int) -> int:
    """
    Get count of unread notifications for a user
    """
    return Notification.get_unread_count(recipient_id = user_id)
