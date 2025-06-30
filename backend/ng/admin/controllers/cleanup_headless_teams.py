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
        "message": f"Cleanup complete. Fixed {fixed_count} headless teams.",
    }
