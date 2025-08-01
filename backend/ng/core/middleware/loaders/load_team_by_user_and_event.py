from functools import wraps
from collections.abc import Callable
from ._util import check_output_exists, get_model_class
from ...exceptions import NotFoundError

def load_team_by_user_and_event(output_key="team") -> Callable:
    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            check_output_exists(kwargs, output_key)
            Team = get_model_class("Team")

            current_user = kwargs.get("current_user")
            event = kwargs.get("event")
            if not current_user or not event:
                raise ValueError("User and event must be loaded first")
            team = Team.find_by_user_and_event(user_id=current_user.id, event_id=event.id)

            if not team:
                raise NotFoundError(f"Team not found for user {current_user.id} and event {event.id}")


            kwargs[output_key] = team
            return f(*args, **kwargs)

        return decorated_function

    return decorator
