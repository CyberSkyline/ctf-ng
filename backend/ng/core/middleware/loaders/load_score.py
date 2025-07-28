from functools import wraps
from collections.abc import Callable
from ._util import check_output_exists, get_model_class


def load_score_by_team_and_event(output_key="score") -> Callable:
    """
    Load score by team and event from the request context.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, team, event, **kwargs):
            check_output_exists(kwargs, output_key)
            Score = get_model_class("Score")
            
            score = Score.find_by_team(team_id=team.id)
            
            kwargs[output_key] = score
            return f(*args, team=team, event=event, **kwargs)
            
        return decorated_function
    return decorator
