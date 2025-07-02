"""
Contains the business logic for an admin tool
that finds and fixes teams without a captain.
"""

from typing import Any

from ...team.models.Team import Team


def cleanup_headless_teams() -> dict[str, Any]:
    """Finds and fixes teams without a captain due to user deletion."""
    fixed_count = Team.fix_headless_teams()

    return {
        "headless_teams_fixed": fixed_count,
        "cleanup_completed": True,
    }
