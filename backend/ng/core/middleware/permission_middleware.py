from functools import wraps
from flask import request
from CTFd.utils.user import get_current_user
from ..utils.api import error_response
from ..utils.logger import get_logger
from ...permissions.controllers.get_team_management_permissions import get_team_management_permissions
from ...permissions.controllers.get_user_permissions import get_user_permissions

logger = get_logger(__name__)


def get_user_role_permissions(f):
    """
    Decorator to retrieve user role permissions and attach them to the request context.
    This allows access to user permissions in the view function.

    The retrieved permissions are attached to kwargs as 'permissions'.
    """
    
    @wraps(f)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return error_response("User not authenticated", "unauthorized", 401)
        response = get_user_permissions(user)
        if "error" in response:
            return error_response(response["error"], "user_permissions", 400)
        if kwargs.get('permissions') is None:
            kwargs['permissions'] = [permission.name for permission in response["permissions"]]
        else:
            kwargs['permissions'].extend([permission.name for permission in response["permissions"]])
        return f(*args, **kwargs)
    return wrapped




def check_user_can_edit_team(f):
    """
    Decorator to check if the current user can edit the specified team.
    The team ID is expected to be provided in the request parameters.

    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return error_response("User not authenticated", "unauthorized", 401)
        
        team_id = request.view_args.get('team_id') or request.args.get('team_id')
        if not team_id:
            return error_response("Team ID is required", "bad_request", 400)
        response = get_team_management_permissions(team_id,user.id)
        if "error" in response:
            return error_response(response["error"], "team_management", 400)

        if kwargs.get('permissions') is None:
            kwargs['permissions'] = [permission.name for permission in response["permissions"]]
        else:
            kwargs['permissions'].extend([permission.name for permission in response["permissions"]])

        return f(*args, **kwargs)

    return wrapped


