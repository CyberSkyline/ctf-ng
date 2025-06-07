# /plugin/utils/decorators.py

from functools import wraps
from flask import request, g
from CTFd.utils.user import get_current_user
from .api_responses import error_response


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
