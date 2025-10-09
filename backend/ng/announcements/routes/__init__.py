"""
Announcement routes package
"""

from .user_routes import announcements_user_namespace
from .admin_routes import announcements_admin_namespace


__all__ = [
    "announcements_user_namespace",
    "announcements_admin_namespace",
]
