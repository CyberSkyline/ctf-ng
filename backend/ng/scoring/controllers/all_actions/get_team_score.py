"""
Retrieves the score details for a specific team.
"""

from typing import Any
from ....core.exceptions import NotFoundError

from ...models import ScoreEvent, Score


def get_team_score(event_id: int, team_id: int, include_history: bool = False) -> dict[str, Any]:
    """
    Get the current score and optionally the scoring history for a team
    """
    score = Score.find_by_team_and_event(team_id=team_id, event_id=event_id)
    if not score:
        raise NotFoundError(f"No score found for team {team_id} in event {event_id}")

    result = {
        "score": score,
        "rank": Score.get_team_rank(team_id=team_id, event_id=event_id),
    }

    if include_history:
        recent_events = ScoreEvent.find_filtered_events(score_id=score.id, limit=10, eager_load_source=True)
        result["recent_events"] = recent_events

    return result
