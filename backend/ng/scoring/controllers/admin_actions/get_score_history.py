"""
Retrieves detailed scoring history for audit purposes.
"""

from typing import Any

from ...models import ScoreEvent


def get_score_history(
    event_id: int,
    team_id: int | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Get scoring history for auditing
    """
    events = ScoreEvent.find_filtered_events(
        event_id=event_id,
        team_id=team_id,
        limit=limit,
        eager_load_source=True,
    )

    return {
        "total_events": len(events),
        "events": events,
        "filters_applied": {
            "event_id": event_id,
            "team_id": team_id,
            "limit": limit,
        },
    }
