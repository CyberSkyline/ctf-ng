"""
Middleware decorators for authentication, authorization, lookup, and request validation.
/backend/ctfd/plugin/core/middleware/middleware.py
"""

from functools import wraps
from flask import request, g
from sqlalchemy.exc import IntegrityError
from CTFd.utils.user import get_current_user
from CTFd.models import db
from ..utils.api_responses import error_response
from ..utils.logger import get_logger
from .utils import (
    params_check_valid,
    get_param_values,
    filter_model_by_fields,
)


logger = get_logger(__name__)

"""
For all lookup decorators, generic/common parameters are expected to be prefixed with 'user_', 'event_', 'team_' or other model in future.
For example, 'user_id', 'event_name', 'team_id'.
This allows the decorator to handle both specific and generic parameter names.
"""


def lookup(model, params: list[str], attach_as: str = None):
    """
    Generic decorator to retrieve a model instance by given parameters.
    Capable of handling both specific and generic parameters.
    As well as parameters present through relationships.
    ie: @lookup(Team, ['event_id', 'user_id']) works because Team has related TeamMembers who have user_ids

    Args:
        model: Model class to query.
        params (list[str]): List of parameter names to check in the request.
        attach_as (str): Name to attach the found instance to kwargs (defaults to model.__name__.lower()).

    The retrieved instance is attached to the `kwargs` as `attach_as`.
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if params_check_valid(params, model) is False:
                return error_response(
                    f"Invalid parameters {params} for model {model.__name__}.",
                    "invalid_parameter",
                    400,
                )

            values_result = get_param_values(params, request)
            if not values_result.success:
                return values_result.error_response

            values = values_result.data

            filter_result = filter_model_by_fields(model, dict(zip(params, values)))
            if not filter_result.success:
                return filter_result.error_response

            attach_name = attach_as or model.__name__.lower()
            kwargs[attach_name] = filter_result.data
            return f(*args, **kwargs)

        return wrapped

    return decorator


def authed_user_required(f):
    """Decorator that ensures user is authenticated and attaches user to g.user"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found in session", "auth", 401)
        g.user = current_user
        return f(*args, **kwargs)

    return decorated_function


def json_body_required(f):
    """Decorator that ensures request has JSON body and attaches it to g.json_data"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return error_response("Request must have a JSON body", "body", 400)
        data = request.get_json()
        if not data:
            return error_response("JSON is malformed or invalid", "body", 400)
        g.json_data = data
        return f(*args, **kwargs)

    return decorated_function


def handle_integrity_error(f):
    """Decorator that wraps controller calls and handles IntegrityError consistently"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
            # Rollback the session to avoid leaving it in a broken state
            db.session.rollback()
            logger.error(
                "Database integrity error in route handler",
                extra={
                    "context": {
                        "function": f.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs),
                        "error": str(e),
                    }
                },
            )
            return error_response(
                "Database constraint error. Please check your request and try again.",
                "database",
                409,
            )

    return decorated_function
