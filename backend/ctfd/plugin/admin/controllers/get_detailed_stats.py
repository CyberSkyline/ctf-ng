"""
/backend/ctfd/plugin/admin/database/get_detailed_stats.py
Contains the business logic to query and assemble a comprehensive statistics report for the system.
"""

from typing import Any

from CTFd.models import db
from sqlalchemy import func

from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from .get_data_counts import get_data_counts
from ...utils.data_conversion import rows_to_dicts


def get_detailed_stats() -> dict[str, Any]:
    """Gets detailed stats including per event breakdowns and empty teams.

    Returns:
        dict: Detailed stats with event data and potential issues.
    """

    event_stats_query = (
        db.session.query(
            Event.id,
            Event.name,
            func.count(Team.id.distinct()).label("teams"),
            func.count(TeamMember.id).label("total_members"),
        )
        .outerjoin(Team, Event.id == Team.event_id)
        .outerjoin(TeamMember, Event.id == TeamMember.event_id)
        .group_by(Event.id, Event.name)
        .all()
    )

    event_stats = rows_to_dicts(event_stats_query)

    empty_teams_query = db.session.query(Team.id, Team.name, Team.event_id).filter(Team.member_count == 0).all()

    empty_teams = [
        {"id": team_id, "name": team_name, "event_id": event_id} for team_id, team_name, event_id in empty_teams_query
    ]

    return {
        "success": True,
        "overview": get_data_counts(),
        "events": event_stats,
        "empty_teams": empty_teams,
        "total_empty_teams": len(empty_teams),
    }
