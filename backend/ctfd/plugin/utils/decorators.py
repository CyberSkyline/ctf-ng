# /plugin/utils/decorators.py

from functools import wraps
from flask import request, g
from CTFd.utils.user import get_current_user
from sqlalchemy.exc import IntegrityError
from .api_responses import error_response
from .logger import get_logger


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
