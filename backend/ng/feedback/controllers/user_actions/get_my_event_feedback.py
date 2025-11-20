"""
Retrieves event feedback
"""

from ...models import Feedback


def get_my_event_feedback(
    user_id: int,
    event_id: int
) -> Feedback | None:
    return Feedback.query.filter_by(
        user_id = user_id,
        event_id = event_id,
        challenge_id = None
    ).first()
