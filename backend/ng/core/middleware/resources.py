"""
Middleware System
This makes every route clean and short
"""

from functools import wraps
from flask import g
from ..exceptions import NotFoundError
from ..utils import get_models

def load_target_member():
    """Load target team member from team_id (URL) or user_id (request body)"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            if not hasattr(g, "team"):
                raise ValueError("Team must be loaded first (@load_team)")
            user_id = kwargs.get("user_id")
            if not user_id:
                if not hasattr(g, "json_data"):
                    raise ValueError("user_id required in URL or JSON request body")
                user_id = g.json_data.get("user_id")
            if not user_id:
                raise ValueError("user_id is missing or empty")
            target_member = models["TeamMember"].find_by_user_and_team(user_id, g.team.id)
            if not target_member:
                raise NotFoundError("User is not a member of this team")
            g.target_member = target_member
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def load_tags_from_request(field_name="tag_ids"):
    """
    Load TicketTag objects from a list of IDs in the request body.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            if not hasattr(g, "validated_data"):
                raise ValueError("Validated data required - use validation middleware first")

            tag_ids = g.validated_data.get(field_name)
            if not tag_ids:
                raise ValueError(f"Field '{field_name}' is required in validated data")

            tags = []
            for tag_id in tag_ids:
                tag = models["TicketTag"].find_by_id(tag_id)
                if not tag:
                    raise NotFoundError(f"Tag with ID {tag_id} not found")
                tags.append(tag)

            g.tags = tags
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ============ COMPOSITE LOADERS ============


def load_team_and_event():
    """Load team from URL and its associated event"""

    def decorator(f):
        @load_team()
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            event = models["Event"].find_by_id(g.team.event_id)
            if not event:
                raise NotFoundError(f"Event with ID {g.team.event_id} not found")
            g.event = event
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def load_user_team_in_event():
    """Load user's team membership in the specified event with related objects"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            if not hasattr(g, "validated_data"):
                raise ValueError("Validated data required - use validation middleware first")
            event_id = g.validated_data.get("event_id")
            if not event_id:
                raise ValueError("event_id required in request body")
            event = models["Event"].find_by_id(event_id)
            if not event:
                raise NotFoundError(f"Event with ID {event_id} not found")
            team_member = models["TeamMember"].find_by_user_and_event(g.user.id, event_id)
            if not team_member:
                raise NotFoundError("User is not in any team for this event")
            team = models["Team"].find_by_id(team_member.team_id)
            if not team:
                raise NotFoundError("Team not found")
            g.event = event
            g.team_member = team_member
            g.team = team
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def load_team_and_event_by_invite():
    """Load team by invite code and its associated event"""

    def decorator(f):
        @load_team_by_invite_code()
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            event = models["Event"].find_by_id(g.team.event_id)
            if not event:
                raise NotFoundError(f"Event with ID {g.team.event_id} not found")
            g.event = event
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ============ COMPLEX VALIDATION ============


def load_associations_from_request():
    """Validate optional event_id, team_id, challenge_id in request body"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            if not hasattr(g, "json_data"):
                return f(*args, **kwargs)
            data = g.json_data
            if "event_id" in data and data["event_id"] and data["event_id"] != 0:
                if not models["Event"].find_by_id(data["event_id"]):
                    raise NotFoundError(f"Event with ID {data['event_id']} not found")

            if "team_id" in data and data["team_id"] and data["team_id"] != 0:
                if not models["Team"].find_by_id(data["team_id"]):
                    raise NotFoundError(f"Team with ID {data['team_id']} not found")
            return f(*args, **kwargs)

        return decorated_function

    return decorator

def load_user_teams():
    """Load user teams for user routes"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            if not hasattr(g, "target_user"):
                raise ValueError("User must be loaded first (@load_user)")
            teams = models["User"].get_user_teams_data(g.target_user.id)
            g.user_teams_data = teams
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def load_user_event_team_data():
    """Load user's team in specific event"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            if not hasattr(g, "target_user"):
                raise ValueError("User must be loaded first (@load_user)")
            if not hasattr(g, "event"):
                raise ValueError("Event must be loaded first (@load_event)")
            team_data = models["User"].get_user_teams_in_event_data(g.target_user.id, g.event.id)
            g.user_event_team_data = team_data
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def load_user_details():
    """Load detailed user info for admin"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            models = get_models()
            if not hasattr(g, "target_user"):
                raise ValueError("User must be loaded first (@load_user)")
            user_details = models["User"].get_user_details_by_id(g.target_user.id)
            g.user_data = user_details
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ============ SMART CURRENT USER OPERATIONS ============


def load_current_user_as_target():
    """Set current user as target user for 'me' routes"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "user"):
                raise ValueError("User must be authenticated first")
            g.target_user = g.user
            return f(*args, **kwargs)

        return decorated_function

    return decorator
