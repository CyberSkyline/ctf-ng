"""
Scoring Routes Package
"""

from .admin_routes import scoring_admin_namespace
from .user_routes import scoring_user_namespace

__all__ = [
    "scoring_admin_namespace",
    "scoring_user_namespace",
]
