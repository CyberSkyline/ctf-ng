"""
Transfers captain role from current captain to another member.
"""

from flask import g
from typing import Any

from ..models.TeamMember import TeamMember


def transfer_captaincy(team_id: int, new_captain_id: int, actor_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Transfers captain role from current captain to another member.

    Returns:
        dict: Success status and updated team objects
    """
    team = g.team
    new_captain_team_member = g.target_member

    existing_captain = TeamMember.find_captain_by_team(team.id)

    TeamMember.transfer_captain_role(
        team_id=team.id,
        old_captain_id=existing_captain.id if existing_captain else None,
        new_captain_id=new_captain_team_member.id,
    )

    return {
        "team": team,
        "new_captain": new_captain_team_member,
        "former_captain": existing_captain,
    }
