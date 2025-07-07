"""
Retrieves all team memberships for a user across all events.
"""

from typing import Any
from ..models.User import User

def get_user_teams(user: User) -> list[Any]:
    """Gets all team members for a user across all events.

    """
    return user.get_all_team_memberships()