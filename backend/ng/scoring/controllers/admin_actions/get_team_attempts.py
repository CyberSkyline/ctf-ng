"""
Gets all attempts for a team in an event
"""

from ...models import Attempt


def get_team_attempts(team_id: int, event_id: int) -> list[Attempt]:
    """
    Get all attempts (correct and incorrect) for a team in an event
    """
    return Attempt.find_filtered_attempts(
        team_id = team_id,
        event_id = event_id
    )
