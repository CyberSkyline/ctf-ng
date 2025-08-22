"""
Gets all manual point awards for a team in an event
"""

from ...models import ManualPointAward


def get_team_manual_awards(team_id: int,
                           event_id: int) -> list[ManualPointAward]:
    """
    Get all manual point awards for a team in an event
    """
    return ManualPointAward.find_by_team_and_event(team_id, event_id)
