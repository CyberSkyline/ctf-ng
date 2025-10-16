from functools import wraps
from collections.abc import Callable
from ._util import check_output_exists, get_model_class


def load_score_by_team(output_key="score") -> Callable:
    """
    Load score by team from the request context.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            check_output_exists(kwargs, output_key)
            Score = get_model_class("Score")
            team = kwargs.get("team")
            if not team:
                raise ValueError("Team must be loaded first")

            score = Score.find_by_team(team_id=team.id)

            kwargs[output_key] = score
            return f(*args, **kwargs)

        return decorated_function
    return decorator
