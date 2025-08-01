"""
Support Routes Namespace Package
"""

from .admin_routes import support_admin_namespace
from .user_routes import support_user_namespace

__all__ = [
    "support_admin_namespace",
    "support_user_namespace",
]
