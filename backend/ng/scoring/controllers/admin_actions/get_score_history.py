"""
Retrieves detailed scoring history for audit purposes.
"""

from .... import config
from ...models import ScoreEvent


def get_score_history(
    event,
    team,
    limit: int = config.DEFAULT_SCORE_HISTORY_LIMIT,
) -> list[ScoreEvent]:
    """
    Get scoring history for auditing
    """
    events = ScoreEvent.find_filtered_events(
        event_id=event.id,
        team_id=team.id,
        eager_load_source=True,
    )

    # Apply limit manually since we removed it from the model method
    if limit and len(events) > limit:
        events = events[:limit]

    return events
