from functools import wraps
from collections.abc import Callable
from ._util import check_output_exists, get_model_class
from ...exceptions import NotFoundError


def load_score_by_team_and_event(output_key="score") -> Callable:
    """
    Load score by team and event from the request context.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            check_output_exists(kwargs, output_key)
            Score = get_model_class("Score")
            
            team = kwargs.get("team")
            event = kwargs.get("event")
            
            if not team or not event:
                raise ValueError("Team and event must be loaded first")
                
            score = Score.find_by_team_and_event(team_id=team.id, event_id=event.id)
            
            kwargs[output_key] = score
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator
