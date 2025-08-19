from ...models import Attempt
from ....import config

def get_team_attempts(event, team, limit=config.DEFAULT_SCORE_HISTORY_LIMIT):
    """Get all scoring attempts for a specific team in an event.

    Args:
        event (Event): The event object.
        team (Team): The team object.

    Returns:
        list: A list of scoring attempts for the team.
    """
    return Attempt.query.filter_by(event_id=event.id, team_id=team.id).limit(limit).all()