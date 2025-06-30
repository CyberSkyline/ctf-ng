"""
Pure permission checking middleware - assumes resources are already loaded in g.
"""

from functools import wraps
from flask import g
from CTFd.utils.user import get_current_user, is_admin
from ..exceptions import PermissionError


def _get_models():
    """Lazy import of models to avoid SQLAlchemy table creation during import."""
    from ...team.models.Team import Team
    from ...team.models.TeamMember import TeamMember
    from ...user.models.User import User

    return {"Team": Team, "TeamMember": TeamMember, "User": User}


def require_user_access():
    """Check if current user can access the loaded user's data"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "target_user"):
                raise ValueError("No user loaded - use @load_user first")
            if is_admin():
                return f(*args, **kwargs)
            current_user = get_current_user()
            if not current_user or g.target_user.id != current_user.id:
                raise PermissionError("You can only access your own user data")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


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


def require_team_captain():
    """Check if current user is captain of the loaded team"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = _get_models()
            if not hasattr(g, "team"):
                raise ValueError("No team loaded - use @load_team first")
            if is_admin():
                return f(*args, **kwargs)
            current_user = get_current_user()
            if not current_user:
                raise PermissionError("Authentication required")
            is_captain = models["TeamMember"].find_captain_by_team_and_user(g.team.id, current_user.id)
            if not is_captain:
                raise PermissionError("You must be the team captain to perform this action")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_team_member_management():
    """Check if user can manage members of the loaded team"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = _get_models()
            if not hasattr(g, "team"):
                raise ValueError("No team loaded - use @load_team first")
            if is_admin():
                return f(*args, **kwargs)
            current_user = get_current_user()
            if not current_user:
                raise PermissionError("Authentication required")
            is_captain = models["TeamMember"].find_captain_by_team_and_user(g.team.id, current_user.id)
            if not is_captain:
                raise PermissionError("You must be the team captain to manage team members")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_team_join_eligibility():
    """Special permission check for team joining - loads eligibility data"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = _get_models()
            if not hasattr(g, "event"):
                raise ValueError("Team and event must be loaded first")
            current_user = get_current_user()
            if not current_user:
                raise PermissionError("Authentication required")
            can_join = models["User"].check_can_join_team_in_event(current_user.id, g.event.id)
            current_team_name = None
            if not can_join:
                existing_member = models["TeamMember"].find_by_user_and_event(current_user.id, g.event.id)
                if existing_member:
                    existing_team = models["Team"].find_by_id(existing_member.team_id)
                    current_team_name = existing_team.name if existing_team else "Unknown"
            g.user_eligibility = {
                "can_join": can_join,
                "current_team_name": current_team_name,
            }
            return f(*args, **kwargs)

        return decorated_function

    return decorator
