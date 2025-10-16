"""
Awards manual points to a team.
"""

from ...models import ManualPointAward
from ....notifications.services import NotificationService


def award_manual_points(
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
    )

    # Notify all event participants to refetch leaderboard
    NotificationService._emit_refetch(
        path=f"/ng/scoring/{team.event_id}/leaderboard",
        event_id=team.event_id,
    )

    return award
