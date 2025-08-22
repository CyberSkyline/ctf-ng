"""
Gets all hint redemptions for a team in an event
"""

from ...models import HintRedemption


def get_team_hint_redemptions(team_id: int,
                              event_id: int) -> list[HintRedemption]:
    """
    Get all hint redemptions for a team in an event
    """
    return HintRedemption.find_by_team_and_event(team_id, event_id)
