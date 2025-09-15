"""
Mark notifications as read
"""

from ...models import Notification


def mark_notification_read(notification: Notification) -> Notification:
    """
    Mark a single notification as read
    """
    notification.mark_as_read()
    return notification


def mark_all_read(user_id: int) -> int:
    """
    Mark all notifications as read for a user
    """
    return Notification.mark_all_as_read(recipient_id = user_id)
