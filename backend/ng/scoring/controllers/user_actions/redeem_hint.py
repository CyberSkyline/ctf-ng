"""
Handles hint redemption for challenges.
"""

from typing import Any
from ....core.exceptions import BusinessLogicError
from ....team.models.Team import Team
from ....challenge.models.Hint import Hint

from ...models import HintRedemption


def redeem_hint(
    event_id: int,
    challenge_id: int,
    hint_id: int,
    current_user_id: int,
) -> dict[str, Any]:
    """
    Redeem a hint for a challenge
    """
    team = Team.find_by_user_and_event(current_user_id, event_id)
    if not team:
        raise BusinessLogicError("You must be part of a team in this event to redeem hints")

    redemption = HintRedemption.create_redemption(
        hint_id=hint_id,
        user_id=current_user_id,
        team_id=team.id,
        event_id=event_id,
        challenge_id=challenge_id,
    )

    hint = Hint.query.get(hint_id)

    return {
        "redemption": redemption,
        "hint_body": hint.body,
        "points_deducted": abs(redemption.points),
    }
