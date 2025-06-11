"""
/backend/ctfd/plugin/user/controllers/can_join_team_in_event.py
Checks if a user is eligible to join a team in a specific event.
"""

from typing import Any

from ...team.models.TeamMember import TeamMember


def can_join_team_in_event(user_id: int, event_id: int) -> dict[str, Any]:
    """Checks if a user can join a team in the event.

    Args:
        user_id (int): The user ID.
        event_id (int): The event ID to check eligibility for.

    Returns:
        dict: Success status, eligibility boolean, and reason if not eligible.
    """

    existing_team_member = TeamMember.query.filter_by(user_id=user_id, event_id=event_id).first()

    return {
        "success": True,
        "can_join": existing_team_member is None,
        "reason": ("User already in a team for this event" if existing_team_member else None),
    }
