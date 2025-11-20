"""
Get challenge feedback
"""

from ...models import Feedback


def list_challenge_feedback(challenge_id: int) -> list[Feedback]:
    return Feedback.find_filtered_feedback(
        challenge_id = challenge_id
    )
