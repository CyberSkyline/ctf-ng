"""
Contains the business logic to query and assemble a comprehensive statistics report for the system.
/backend/ctfd/plugin/admin/controllers/get_detailed_stats.py
"""

from typing import Any

from CTFd.models import db
from sqlalchemy import func

from plugin.event.models.Event import Event
from plugin.team.models.Team import Team
from plugin.team.models.TeamMember import TeamMember
from plugin.core.utils.data_conversion import rows_to_dicts
from .get_data_counts import get_data_counts


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

    empty_teams = Team.find_empty_teams()

    return {
        "success": True,
        "overview": get_data_counts(),
        "events": event_stats,
        "empty_teams": empty_teams,
        "total_empty_teams": len(empty_teams),
    }
