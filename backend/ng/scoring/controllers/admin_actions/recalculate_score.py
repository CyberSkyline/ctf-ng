"""
Recalculates scores from scratch (if needed)
"""

from ...models import Score


def recalculate_score(score) -> Score:
    """
    Recalculate a team's score from all ScoreEvents
    """
    score.recalculate()

    return score
