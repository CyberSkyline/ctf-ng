"""
Mark notifications as read
"""

from ....core.exceptions import (
        NotFoundError,
        PermissionError,
        )
from ...models import Notification


def mark_notification_read(
        notification_id: int,
        user_id: int,
        ) -> Notification:
    """
    Mark a single notification as read.
    """
    notification = Notification.find_by_id(notification_id)

    if not notification:
        raise NotFoundError(f"Notification {notification_id} not found")

    if notification.recipient_id != user_id:
        raise PermissionError(
                "You cannot mark other users' notifications as read"
                )

    notification.mark_as_read()
    return notification


def mark_all_read(user_id: int) -> int:
    """
    Mark all notifications as read for a user
    """
    return Notification.mark_all_as_read(recipient_id = user_id)
