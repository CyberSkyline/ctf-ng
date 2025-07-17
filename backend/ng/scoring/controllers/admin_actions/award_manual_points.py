"""
Awards manual points to a team.
"""

from typing import Any
from ....core.exceptions import NotFoundError

from ...models import ManualPointAward, Score


def award_manual_points(
    event_id: int,
    team_id: int,
    points: int,
    reason: str,
    admin_id: int,
) -> dict[str, Any]:
    """
    Award manual points to a team (can be positive or negative)
    """
    score = Score.find_by_team_and_event(team_id=team_id, event_id=event_id)
    if not score:
        raise NotFoundError(f"Team {team_id} has no score in event {event_id}")
    
    previous_points = score.points
    
    award = ManualPointAward.create_award(
        admin_id=admin_id,
        team_id=team_id,
        points=points,
        reason=reason,
        event_id=event_id,
    )
    
    return {
        "award": award,
        "updated_score": score,
        "previous_points": previous_points,
        "new_points": score.points,
    }
