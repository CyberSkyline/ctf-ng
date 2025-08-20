"""
Gets submission history for a team including all scoring events
"""

from typing import Any

from .... import config
from ....scoring.models import (
    ScoreEvent,
    Attempt,
    HintRedemption,
    ManualPointAward,
)


def get_submission_history(
    team_id: int,
    event_id: int,
    limit: int = config.DEFAULT_SUBMISSION_HISTORY_LIMIT
) -> dict[str,
          Any]:
    """
    Get submission history for a team
    """
    return {
        "score_events":
        ScoreEvent.find_filtered_events(
            team_id = team_id,
            event_id = event_id,
            limit = limit,
            eager_load_source = True
        ),
        "attempts":
        Attempt.find_filtered_attempts(
            team_id = team_id,
            event_id = event_id
        ),
        "hint_redemptions":
        HintRedemption.find_filtered_redemptions(
            team_id = team_id
        ),
        "manual_awards":
        ManualPointAward.find_filtered_awards(
            team_id = team_id,
            event_id = event_id,
            limit = limit
        )
    }
