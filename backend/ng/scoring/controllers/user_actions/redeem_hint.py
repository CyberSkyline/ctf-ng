"""
Handles hint redemption for challenges.
"""

from ...models import HintRedemption


def redeem_hint(
    event,
    challenge,
    hint,
    team,
    current_user,
) -> dict:
    """
    Redeem a hint for a challenge
    """
    HintRedemption.create_redemption(
        hint_id=hint.id,
        user_id=current_user.id,
        team_id=team.id,
        challenge_id=challenge.id,
    )

    return hint.serialize(team=team)
