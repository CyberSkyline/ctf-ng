"""
Get challenge progress for a team in an event
"""

from typing import Any

from ....scoring.models import Attempt
from ....challenge.models import Challenge


def get_challenge_progress(event_id: int, team_id: int) -> list[dict[str, Any]]:
    """
    Get challenge progress for a team in an event
    """
    challenges = Challenge.query.filter_by(event_id = event_id).all()
    results = []

    for challenge in challenges:
        attempts = Attempt.find_filtered_attempts(
            team_id = team_id,
            challenge_id = challenge.id
        )

        correct_attempts = [a for a in attempts if a.is_correct]
        unique_questions_solved = len({a.question_id for a in correct_attempts})
        total_points_scored = sum(a.points for a in correct_attempts)

        unique_questions_attempted = len({a.question_id for a in attempts})

        results.append({
            "challenge_id": challenge.id,
            "challenge_name": challenge.name,
            "challenge_icon": challenge.icon,
            "total_points_available": sum(q.points for q in challenge.questions),
            "total_points_scored": total_points_scored,
            "num_questions_solved": unique_questions_solved,
            "num_questions_available": len(challenge.questions),
            "num_attempts_made": len(attempts),
            "num_unique_questions_attempted": unique_questions_attempted,
            "is_completed": unique_questions_solved == len(challenge.questions)
        })

    return results
