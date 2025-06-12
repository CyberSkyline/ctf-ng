"""
/backend/ctfd/plugin/team/controllers/get_team_info.py
Retrieves detailed information about a team and its members.
"""

from typing import Any

from ...event.models.Event import Event
from ..models.Team import Team
from ..models.TeamMember import TeamMember


def get_team_info(team_id: int) -> dict[str, Any]:
    """Gets detailed info about a team.

    Args:
        team_id (int): The team ID to get info for.

    Returns:
        dict: Success status, team details, and membership info.
    """
    team = Team.query.get(team_id)
    if not team:
        return {"success": False, "error": "Team not found."}

    event = Event.query.get(team.event_id)
    team_members = TeamMember.query.filter_by(team_id=team_id).all()

    team_data = {
        "id": team.id,
        "name": team.name,
        "event_id": team.event_id,
        "event_name": event.name if event else "Unknown",
        "member_count": team.member_count,
        "max_team_size": event.max_team_size if event else 0,
        "is_full": team.member_count >= (event.max_team_size if event else 0),
        "invite_code": team.invite_code,
        "ranked": team.ranked,
    }

    return {
        "success": True,
        "team": team_data,
        "team_members": [{"user_id": m.user_id, "joined_at": m.joined_at, "role": m.role} for m in team_members],
    }
