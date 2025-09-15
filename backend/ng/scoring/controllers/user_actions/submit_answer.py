"""
Handles answer submission for challenges.
"""

from ...models import Attempt
from ....notifications.services import NotificationService


def submit_answer(
    event,
    challenge,
    question,
    team,
    current_user,
    submission: str,
) -> Attempt:
    """
    Submit an answer to a challenge question
    """
    attempt = Attempt.create_attempt(
        user_id=current_user.id,
        team_id=team.id,
        challenge_id=challenge.id,
        question_id=question.id,
        submission=submission,
    )

    NotificationService.broadcast_attempt_update(
        event_id=event.id,
        team_id=team.id,
        challenge_id=challenge.id,
        question_id=question.id,
    )

    return attempt
