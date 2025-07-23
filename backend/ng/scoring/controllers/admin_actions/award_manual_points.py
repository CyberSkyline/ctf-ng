"""
Awards manual points to a team.
"""

from ...models import ManualPointAward


def award_manual_points(
    event,
    team,
    score,
    points: int,
    reason: str,
    admin_id: int,
) -> ManualPointAward:
    """
    Award manual points to a team (can be positive or negative)
    """
    award = ManualPointAward.create_award(
        admin_id=admin_id,
        team_id=team.id,
        points=points,
        reason=reason,
        event_id=event.id,
    )

    return award
