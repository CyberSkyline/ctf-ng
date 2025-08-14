from functools import wraps
from collections.abc import Callable
from ._util import LoaderType, get_model_class, get_json_val, get_param_val
from ...exceptions import NotFoundError

def load_indvidual_container_by_user(source: LoaderType = LoaderType.PARAM, input_key="user_id", output_key="indvidual_container") -> Callable:
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            IndvidualContainer = get_model_class("IndvidualContainer")
            print(IndvidualContainer)
            if source == LoaderType.PARAM:
                user_id = get_param_val(kwargs, input_key)
            elif source == LoaderType.BODY:
                user_id = get_json_val(kwargs, input_key)
            else:
                raise ValueError(f"Invalid loader type: {source}")

            indvidual_container = IndvidualContainer.get_user_indvidual_container(user_id)

            if not indvidual_container:
                raise NotFoundError(f"Invalid user: {user_id}")

            kwargs[output_key] = indvidual_container
            return f(*args, **kwargs)

        return decorated_function
    return decorator
