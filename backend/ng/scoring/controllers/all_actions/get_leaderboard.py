"""
Retrieves the leaderboard for an event.
"""

from typing import Any

from ...models import Score


def get_leaderboard(event_id: int, limit: int | None = 100) -> list[dict[str, Any]]:
    """
    Retrieves the cached leaderboard for a given event
    """
    leaderboard_data = Score.get_leaderboard(event_id=event_id, limit=limit)
    return leaderboard_data
