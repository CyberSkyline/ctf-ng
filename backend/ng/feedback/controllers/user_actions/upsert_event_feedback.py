"""
Upsert event feedback
"""

from typing import Any

from ...models import Feedback


def upsert_event_feedback(
    user_id: int,
    event_id: int,
    feedback_data: dict[str,
                        Any],
) -> Feedback:
    existing = Feedback.query.filter_by(
        user_id = user_id,
        event_id = event_id,
        challenge_id = None
    ).first()

    if existing:
        existing.update_feedback(feedback_data)
        return existing

    return Feedback.create_feedback(
        user_id = user_id,
        event_id = event_id,
        feedback_data = feedback_data,
    )
