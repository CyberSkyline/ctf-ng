"""
Gets score events timeline for a team with embedded source data
"""

from typing import Any

from ...models import ScoreEvent


def get_team_score_events(
    team_id: int,
    event_id: int,
) -> list[dict[str,
               Any]]:
    """
    Get score events timeline for a team with embedded source data
    """
    score_events = ScoreEvent.find_filtered_events(
        team_id = team_id,
        event_id = event_id,
        eager_load_source = True
    )
    return [
        event.serialize(include_admin_fields = True) for event in score_events
    ]
