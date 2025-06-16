from functools import wraps
from flask import request, abort,g
from plugin.user.models.User import User
from plugin.event.models.Event import Event
from plugin.team.models.Team import Team
from CTFd.utils.user import get_current_user
from sqlalchemy.exc import IntegrityError
from plugin.utils.api_responses import error_response
from plugin.utils.logger import get_logger
from sqlalchemy import and_

logger = get_logger(__name__)

def lookup_user(params: list[str]):
    """Decorator to retrieve user by given parameters.

    Args:
        params (list[str]): List of parameter names to check in the request.
    
    Retrieved user is attached to the `kwargs` as `user`.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            values = params_check_valid(params, request, User)
            if len(values) == 1:
                user = User.query.get(values[0])
                if not user:
                    logger.error(f"User with {params} {value} not found.")
                    abort(404, description=f"User with {params} {value} not found.")
            elif len(values) > 1:
                user = filter_model_by_fields(User, dict(zip(params, values)))
                if not user:
                    logger.error(f"User with {params} {values} not found.")
                    abort(404, description=f"User with {params} {values} not found.")
                if len(user) > 1:
                    logger.error(f"Multiple users found with {params} {values}.")
                    abort(400, description=f"Multiple users found with {params} {values}.")
            kwargs["user"] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def lookup_event(params: list[str]):
    """Decorator to retrieve event by given paramseter.
    
    Args:
        params (list[str]): List of parameter names to check in the request.

    Retrieved event is attached to the `kwargs` as `event`.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            value = paramss_check_valid(paramss, request, Event)
            if len(value) == 1:
                event = Event.query.get(value[0])
                if not event:
                    abort(404, description=f"Event with {params} {value[0]} not found.")
            elif len(value) > 1:
                event = filter_model_by_fields(Event, dict(zip(params, value)))
                if not event:
                    abort(404, description=f"Event with {params} {value} not found.")
                if len(event) > 1:
                    abort(400, description=f"Multiple events found with {params} {value}.")
            kwargs["event"] = event
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def lookup_team(params: list[str]):
    """Decorator to retrieve team by given parameters.
    
    Args:
        params (list[str]): List of parameter names to check in the request.

    Retrieved team is attached to the `kwargs` as `team`.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            values = params_check_valid(params, request, Team)
            if len(values) == 1:
                team = Team.query.get(values[0])
                if not team:
                    abort(404, description=f"Team with {params} {values[0]} not found.")
            elif len(values) > 1:
                team = filter_model_by_fields(Team, dict(zip(params, values)))
                if not team:
                    abort(404, description=f"Team with {params} {values} not found.")
                if len(team) > 1:
                    abort(400, description=f"Multiple teams found with {params} {values}.")
            kwargs["team"] = team
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def authed_user_required(f):
    """Decorator that ensures user is authenticated and attaches user to g.user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found in session", "auth", 403)
        g.user = current_user
        return f(*args, **kwargs)
    return decorated_function

def check(f):
    
                              


def json_body_required(f):
    """Decorator that ensures request has JSON body and attaches it to g.json_data"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        if not data:
            return error_response("JSON body is required", "body", 400)
        g.json_data = data
        return f(*args, **kwargs)

    return decorated_function


def handle_integrity_error(f):
    """Decorator that wraps controller calls and handles IntegrityError consistently"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger = get_logger(__name__)
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
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


def params_check_valid(params, request, model):
    logger = get_logger(__name__)
    """Check if the request has valid parameters for the given model."""
    values = []

    for param in params:
        if not hasattr(model, param):
            logger.error(f"Invalid parameter '{param}' for model {model.__name__}.")
            abort(400, description=f"Invalid parameter '{param}' for model {model.__name__}.")
        value = request.view_args.get(param, None)
        if value is None:
            logger.error(f"Missing required parameter '{param}' in request.")
            abort(400, description=f"Missing required parameter '{param}' in request.")
        values.append(value)

    if len(params) == 1:
        column = getattr(model, params[0])
        if not column.unique and not column.primary_key:
            logger.error(f"Single Parameter '{params[0]}' is not unique or primary key in model {model.__name__}.")
            abort(400, description=f"Single Parameter '{params[0]}' must be unique or primary key in model {model.__name__}.")
    
    return values

def filter_model_by_fields(model, filters):
    valid_columns = {col.name for col in model.__table__.columns}
    conditions = [
        getattr(model, key) == value
        for key, value in filters.items()
        if key in valid_columns
    ]
    return db.session.query(model).filter(and_(*conditions)).all()

        
        
                



