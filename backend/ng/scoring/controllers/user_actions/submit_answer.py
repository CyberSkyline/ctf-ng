"""
Handles answer submission for challenges.
"""

from ....core.exceptions import BusinessLogicError
from ....team.models.Team import Team

from ...models import Attempt, Score


def submit_answer(
    event_id: int,
    challenge_id: int,
    question_id: int,
    submission: str,
    current_user_id: int,
) -> dict:
    """
    Submit an answer to a challenge question
    """
    team = Team.find_by_user_and_event(current_user_id, event_id)
    if not team:
        raise BusinessLogicError("You must be part of a team in this event to submit answers")

    attempt = Attempt.create_attempt(
        user_id=current_user_id,
        team_id=team.id,
        event_id=event_id,
        challenge_id=challenge_id,
        question_id=question_id,
        submission=submission,
    )

    score = Score.find_by_team_and_event(team.id, event_id)

    return {
        "is_correct": attempt.is_correct,
        "points_awarded": attempt.points,
        "new_score": score.points if score else 0,
    }
