"""
Updates team information with proper authorization checks.
"""

from flask import g
from typing import Any

from ...core.validation import validate_unique_name
from ...core.utils import build_conditional_update_data

from ..models.Team import Team


def update_team(
    team_id: int,
    actor_id: int,
    new_name: str | None = None,
    is_admin: bool = False,
) -> dict[str, Any]:
    """Updates team info with auth checks.

    Returns:
        dict: Success status and updated team object.
    """
    team = g.team

    if new_name:
        validate_unique_name(
            Team,
            new_name,
            current_object=team,
            scope_field="event_id",
            scope_value=team.event_id,
            error_message=f"A team with the name '{new_name}' already exists in this event",
        )

    update_data = build_conditional_update_data(
        team, name=(new_name, new_name and new_name.strip() and new_name != team.name)
    )

    if update_data:
        team.update_name(new_name, commit=True)

    return {
        "team": team,
        "updated": True,
    }
