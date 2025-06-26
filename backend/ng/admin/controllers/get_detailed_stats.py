"""
Contains the business logic to query and create a statistics report.
"""

from typing import Any
from CTFd.models import db
from sqlalchemy import func

from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...core.utils.data_conversion import rows_to_dicts
from ...core.utils.api_responses import serialize_item_datetimes
from .get_data_counts import get_data_counts


def get_detailed_stats() -> dict[str, Any]:
    """Gets detailed stats including per event breakdowns and empty teams."""

    event_stats_query = (
        db.session.query(
            Event.id,
            Event.name,
            Event.start_time,
            Event.end_time,
            func.count(Team.id.distinct()).label("teams"),
            func.count(TeamMember.id).label("total_members"),
        )
        .outerjoin(Team, Event.id == Team.event_id)
        .outerjoin(TeamMember, Event.id == TeamMember.event_id)
        .group_by(Event.id, Event.name, Event.start_time, Event.end_time)
        .all()
    )

    event_stats_raw = rows_to_dicts(event_stats_query)

    event_stats_serialized = [serialize_item_datetimes(stat) for stat in event_stats_raw]

    empty_teams = Team.find_empty_teams()

    return {
        "success": True,
        "overview": get_data_counts(),
        "events": event_stats_serialized,
        "empty_teams": empty_teams,
        "total_empty_teams": len(empty_teams),
    }
