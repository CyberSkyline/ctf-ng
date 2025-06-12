"""
/backend/ctfd/plugin/user/controllers/get_user_stats.py
Calculates participation statistics for a user across all events.
"""

from typing import Any

from CTFd.models import db

from ...event.models.Event import Event
from ...team.models.TeamMember import TeamMember
from ..models.User import User


def get_user_stats(user_id: int) -> dict[str, Any]:
    """Gets participation stats for a user across all events.

    Args:
        user_id (int): The user ID to get stats for.

    Returns:
        dict: Success status and participation stats.
    """

    user = User.query.get(user_id)
    if not user:
        return {"success": False, "error": "User not found in extended system"}

    # Direct query for distinct event IDs, avoids loading objects
    events_participated_query = db.session.query(TeamMember.event_id.distinct()).filter_by(user_id=user_id).all()
    events_participated = {event_id for (event_id,) in events_participated_query}

    total_events = Event.query.count()

    return {
        "success": True,
        "stats": {
            "total_team_members": TeamMember.query.filter_by(user_id=user_id).count(),
            "events_participated": len(events_participated),
            "total_events_available": total_events,
            "participation_rate": (len(events_participated) / total_events if total_events > 0 else 0),
        },
    }
