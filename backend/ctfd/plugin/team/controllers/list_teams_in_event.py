"""
/backend/ctfd/plugin/team/controllers/list_teams_in_event.py
Retrieves a list of all teams within a specific event.
"""

from typing import Any

from ...event.models.Event import Event
from ..models.Team import Team


def list_teams_in_event(event_id: int) -> dict[str, Any]:
    """Gets all teams in a event with their basic info.

    Args:
        event_id (int): The event ID to list teams from.

    Returns:
        dict: Success status, list of teams with stats, and event info.
    """
    event = Event.query.get(event_id)
    if not event:
        return {
            "success": False,
            "error": f"Event with ID {event_id} does not exist",
        }

    teams = Team.query.filter_by(event_id=event_id).all()

    team_list = []
    for team in teams:
        team_list.append(
            {
                "id": team.id,
                "name": team.name,
                "member_count": team.member_count,
                "max_team_size": event.max_team_size,
                "is_full": team.member_count >= event.max_team_size,
                "invite_code": team.invite_code,
                "ranked": team.ranked,
            }
        )

    return {
        "success": True,
        "teams": team_list,
        "event_name": event.name,
        "total_teams": len(team_list),
    }
