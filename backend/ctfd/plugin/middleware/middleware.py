from functools import wraps
from flask import request, abort
from plugin.user.models.User import User
from plugin.event.models.Event import Event
from plugin.team.models.Team import Team

def user(param)
    def decorator(f)
        @wraps(f)
        def user(*args, **kwargs):
            """Decorator to retrieve user by given parameter."""
            value = request.view_args.get(param, None)
            if not value:
                abort(400, description=f"Valid parameter not found got: {param}")
            
            user = User.query.get(value)
            if not user:
                abort(404, description=f"User with {param} {value} not found.")
            kwargs["user"] = user
            return f(*args, **kwargs)
        return user
    return decorator

def event(param):
    def decorator(f):
        @wraps(f)
        def event(*args, **kwargs):
            """Decorator to retrieve event by given parameter."""
            value = request.view_args.get(param, None)
            if not value:
                abort(400, description=f"Valid parameter not found got: {param}")
            
            event = Event.query.get(value)
            if not event:
                abort(404, description=f"Event with {param} {value} not found.")
            kwargs["event"] = event
            return f(*args, **kwargs)
        return event
    return decorator

def team(param):
    def decorator(f):
        @wraps(f)
        def team(*args, **kwargs):
            """Decorator to retrieve team by given parameter."""
            value = request.view_args.get(param, None)
            if not value:
                abort(400, description=f"Valid parameter not found got: {param}")
            
            team = Team.query.get(value)
            if not team:
                abort(404, description=f"Team with {param} {value} not found.")
            kwargs["team"] = team
            return f(*args, **kwargs)
        return team
    return decorator


