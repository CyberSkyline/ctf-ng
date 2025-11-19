"""
Retrieves challenge feedback
"""

from ...models import Feedback


def get_my_challenge_feedback(
    user_id: int,
    challenge_id: int
) -> Feedback | None:
    return Feedback.query.filter_by(
        user_id = user_id,
        challenge_id = challenge_id
    ).first()
