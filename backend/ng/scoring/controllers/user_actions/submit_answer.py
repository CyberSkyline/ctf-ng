"""
Handles answer submission for challenges.
"""

from ...models import Attempt


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
        event_id=event.id,
        challenge_id=challenge.id,
        question_id=question.id,
        submission=submission,
    )

    return attempt
