"""
Get event feedback
"""

from ...models import Feedback


def list_event_feedback(event_id: int) -> list[Feedback]:
    return (
        Feedback.query.filter_by(
            event_id = event_id,
            challenge_id = None
        ).order_by(Feedback.updated_at.desc()).all()
    )
