"""
Pure permission checking middleware - assumes resources are already loaded in g.
"""

from functools import wraps
from flask import g
from CTFd.utils.user import get_current_user, is_admin
from ..exceptions import PermissionError, BusinessLogicError
from ...core.utils import get_models

def require_ticket_access():
    """Check if current user can access the loaded ticket"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "ticket"):
                raise ValueError("No ticket loaded - use @load_ticket first")
            if is_admin():
                return f(*args, **kwargs)
            current_user = get_current_user()
            if not current_user or g.ticket.author_id != current_user.id:
                raise PermissionError("You do not have permission to access this ticket")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_ticket_update():
    """Check if current user can update the loaded ticket"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "ticket"):
                raise ValueError("No ticket loaded - use @load_ticket first")
            if is_admin():
                return f(*args, **kwargs)
            current_user = get_current_user()
            if not current_user or g.ticket.author_id != current_user.id:
                raise PermissionError("You do not have permission to update this ticket")
            return f(*args, **kwargs)

        return decorated_function

    return decorator

def check_demographic_eligibility():
    """Check if user can register for the event (no existing demographic)"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()

            if not hasattr(g, "user") or not hasattr(g, "event"):
                raise ValueError("User and event must be loaded first")

            existing = models["Demographic"].find_by_user_and_event(g.user.id, g.event.id)

            if existing:
                raise BusinessLogicError("You have already registered for this event")

            return f(*args, **kwargs)

        return decorated_function

    return decorator
