
from functools import wraps
from typing import Callable
from ._util import LoaderType, check_output_exists, get_model_class, get_json_val, get_param_val
from ...exceptions import NotFoundError

def load_team_by_invite_code(source : LoaderType = LoaderType.BODY, input_key="invite_code", output_key="team") -> Callable:
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            check_output_exists(kwargs, output_key)
            Team = get_model_class("Team")
            if source == LoaderType.PARAM:
                invite_code = get_param_val(kwargs, input_key)
            elif source == LoaderType.BODY:
                invite_code = get_json_val(input_key)
            else:
                raise ValueError(f"Invalid loader type: {source}")

            team = Team.find_by_invite_code(invite_code)

            if not team:
                raise NotFoundError(f"Invalid invite code: {invite_code}")

            kwargs[output_key] = team
            return f(*args, **kwargs)

        return decorated_function

    return decorator
