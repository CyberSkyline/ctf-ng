"""
/backend/ctfd/plugin/user/controllers/can_join_team_in_event.py
Checks if a user is eligible to join a team in a specific event.
"""

from typing import Any

from plugin.user.models.User import User


def can_join_team_in_event(user_id: int, event_id: int) -> dict[str, Any]:
    """Checks if a user can join a team in the event.

    Args:
        user_id (int): The user ID.
        event_id (int): The event ID to check eligibility for.

    Returns:
        dict: Success status, eligibility boolean, and reason if not eligible.
    """

    can_join = User.check_can_join_team_in_event(user_id, event_id)

    return {
        "success": True,
        "can_join": can_join,
        "reason": ("User already in a team for this event" if not can_join else None),
    }
