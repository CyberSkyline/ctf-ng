from functools import wraps
from CTFd.utils.user import get_current_user
from ..utils.api import error_response
from ..utils.logger import get_logger
from ...permissions.controllers.get_team_management_permissions import get_team_management_permissions
from ...permissions.controllers.get_user_permissions import get_user_permissions
from ...permissions.controllers.get_challenge_permissions import get_challenge_permissions
from ...event.models.Demographic import Demographic
from ...permissions.models.enums import PermissionEnum, PermissionCheck, DenyReason

logger = get_logger(__name__)



def check_permissions(permission: PermissionEnum, error_message: str):
    def decorator(f):
        """Decorator to get user permissions and append them to the request context."""
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            trace = PermissionCheck()
            if not user:
                trace.add_denial(permission, DenyReason.NOT_AUTHENTICATED)
                return _deny(permission, trace, error_message)
            trace.merge(get_user_permissions(user))
            team = kwargs.get('team')
            if team:
                trace.merge(get_team_management_permissions(team, user))
                trace.merge(get_challenge_permissions(team))
            permissions = list({grant.permission.name for grant in trace.granted})
            if kwargs.get('permissions') is None:
                kwargs['permissions'] = permissions
            else:
                kwargs['permissions'].extend(permissions)
            if permission is not None and permission.name not in permissions:
                return _deny(permission, trace, error_message)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def _deny(permission: PermissionEnum, trace: PermissionCheck, msg: str = "You do not have permission to perform this action"):
    deny = next((d for d in trace.denied if d.permission == permission), None)
    error_message = msg
    if deny:
        error_message += f": {deny.reason.name}"
    return error_response(error_message, "forbidden", 403)

def event_only_public(f):
    """Decorator to ensure the event is public."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        event = kwargs.get('event')
        current_user = kwargs.get('current_user')
        id = current_user.id if current_user else None
        if Demographic.find_by_user_and_event(id, event.id) is None:
            if not event.public:
                return error_response("Event not found", "not_found", 404)
        return f(*args, **kwargs)
    return wrapped


