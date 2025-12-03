"""
Feedback route package
"""

from .user_routes import feedback_user_namespace
from .admin_routes import feedback_admin_namespace


__all__ = [
    "feedback_user_namespace",
    "feedback_admin_namespace",
]
