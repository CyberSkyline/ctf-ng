"""
Get challenge progress for a team in an event
"""

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import selectinload

from ....scoring.models import Attempt
from ....challenge.models import Challenge


def get_challenge_progress(event_id: int, team_id: int) -> list[dict[str, Any]]:
    """
    Get challenge progress for a team in an event
    """
    challenges = (Challenge.query
        .filter_by(event_id = event_id)
        .options(selectinload(Challenge.questions))
        .all()
    )

    # load all of the team's attempts up front rather than querying once per challenge
    attempts_by_challenge: dict[int, list[Attempt]] = defaultdict(list)
    for attempt in Attempt.query.filter(
        Attempt.team_id == team_id,
        Attempt.challenge_id.in_([c.id for c in challenges]),
    ):
        attempts_by_challenge[attempt.challenge_id].append(attempt)

    results = []

    for challenge in challenges:
        attempts = attempts_by_challenge[challenge.id]

        correct_attempts = [a for a in attempts if a.is_correct]
        unique_questions_solved = len({a.question_id for a in correct_attempts})
        total_points_scored = sum(a.points for a in correct_attempts)

        unique_questions_attempted = len({a.question_id for a in attempts})

        # a challenge with no questions is not complete, otherwise it reports a completion with no completion time
        is_completed = len(challenge.questions) > 0 and unique_questions_solved == len(challenge.questions)
        # the challenge is done when its final question is solved, so the latest correct attempt is the completion time
        completed_at = max((a.timestamp for a in correct_attempts), default=None) if is_completed else None

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
            "is_completed": is_completed,
            "completed_at": completed_at.isoformat() + "Z" if completed_at else None,
        })

    return results
