"""
Recalculates scores from scratch (if needed)
"""

from typing import Any
from ....core.exceptions import NotFoundError

from ...models import Score


def recalculate_score(
    event_id: int,
    team_id: int,
) -> dict[str, Any]:
    """
    Recalculate a team's score from all ScoreEvents
    """
    score = Score.find_by_team_and_event(team_id=team_id, event_id=event_id)
    if not score:
        raise NotFoundError(f"Team {team_id} has no score in event {event_id}")

    old_points = score.points

    score.recalculate()

    return {
        "team_id": team_id,
        "event_id": event_id,
        "old_points": old_points,
        "new_points": score.points,
        "difference": score.points - old_points,
        "last_update": score.last_update,
    }
