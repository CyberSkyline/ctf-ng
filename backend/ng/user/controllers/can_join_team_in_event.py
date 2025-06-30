"""
Checks if a user is eligible to join a team in a specific event.
"""

from flask import g
from typing import Any
from ...core import BusinessLogicError


def can_join_team_in_event(user_id: int, event_id: int) -> dict[str, Any]:
    """Checks if a user can join a team in the event.

    Returns:
        dict: Success status, eligibility boolean, and reason if not eligible.
    """

    eligibility = g.user_eligibility

    if not eligibility["can_join"]:
        raise BusinessLogicError("User is already in a team for this event")

    return {"can_join": True, "message": "User is eligible to join a team."}
