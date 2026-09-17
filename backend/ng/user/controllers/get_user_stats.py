"""
Business logic for computing platform-wide statistics for a user.
"""

from typing import Any

from CTFd.models import db
from sqlalchemy import and_, func

from ...challenge.models import Challenge, Question
from ...event.models import Event
from ...scoring.models.Attempt import Attempt
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ..models.User import User


def get_user_stats(user: User) -> dict[str, Any]:
    """
    Get platform-wide statistics for a user.
    """
    # Number of correct attempts
    total_correct_submissions = Attempt.query.filter_by(user_id=user.id, is_correct=True).count()

    # Total number of non-practice events the user has started
    events_participated = (
        db.session.query(func.count(TeamMember.id))
        .join(Team, TeamMember.team_id == Team.id)
        .join(Event, TeamMember.event_id == Event.id)
        .filter(
            TeamMember.user_id == user.id,
            Team.start_timestamp.isnot(None),
            Event.practice.is_(False),
        )
        .scalar()
    )

    # Number of practice challenges where no question has not been answered correctly (all questions completed.)
    # Double negative is the most straightforward way to express this query.
    practice_challenges_completed = (
        Challenge.query
        .join(Event, Challenge.event_id == Event.id)
        .filter(
            Event.practice.is_(True),
            Challenge.questions.any(),
            ~Challenge.questions.any(
                ~Question.attempts.any(and_(Attempt.user_id == user.id, Attempt.is_correct.is_(True)))
            ),
        )
        .count()
    )

    return {
        "total_correct_submissions": total_correct_submissions,
        "events_participated": events_participated,
        "practice_challenges_completed": practice_challenges_completed,
    }
