"""
Notification routes package
"""

from .user_routes import notifications_user_namespace
from .admin_routes import notifications_admin_namespace


__all__ = [
    "notifications_user_namespace",
    "notifications_admin_namespace",
]
