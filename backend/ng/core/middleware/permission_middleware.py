from functools import wraps
from CTFd.utils.user import get_current_user
from ..utils.api import error_response
from ..utils.logger import get_logger
from ...permissions.controllers.get_team_management_permissions import get_team_management_permissions
from ...permissions.controllers.get_user_permissions import get_user_permissions

logger = get_logger(__name__)



def get_permissions(f):
    """Decorator to get user permissions and append them to the request context."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return error_response("User not authenticated", "unauthorized", 401)
        permissions = get_user_permissions(user)
        team = kwargs.get('team')
        if team:
            permissions.extend(get_team_management_permissions(team, user))
        permissions = list(set([permission.name for permission in permissions]))
        if kwargs.get('permissions') is None:
            kwargs['permissions'] = permissions
        else:
            kwargs['permissions'].extend(permissions)
        return f(*args, **kwargs)
    return wrapped

def event_only_public(f):
    """Decorator to ensure the event is public."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        event = kwargs.get('event')
        if not event or not event.public:
            return error_response("Event not found", "not_found", 404)
        return f(*args, **kwargs)
    return wrapped


