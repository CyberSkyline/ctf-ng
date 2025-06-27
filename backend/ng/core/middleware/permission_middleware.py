from functools import wraps
from flask import request, g
from sqlalchemy.exc import IntegrityError
from CTFd.utils.user import get_current_user
from CTFd.models import db
from ..utils.api_responses import error_response
from ..utils.logger import get_logger
from .models.UserRole import UserRole
from .utils import (
    params_check_valid,
    get_param_values,
    filter_model_by_fields,
)

logger = get_logger(__name__)


def get_user_role_permissions(f):
    """
    Decorator to retrieve user role permissions and attach them to the request context.
    This allows access to user permissions in the view function.

    The retrieved permissions are attached to `g.user_permissions`.
    """
    
    @wraps(f)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return error_response("User not authenticated", "unauthorized", 401)
        user_role = UserRole.get_user_role(user.id)
        if not user_role:
            return error_response("User role not found", "not_found", 404)

        permissions = UserRole.get_permissions(user_role.role)
        if not permissions:
            return error_response("No permissions found for user role", "not_found", 404)
        
        perm_array = [perm.name for perm in permissions]
        kwargs['permissions'] = perm_array

        
        return f(*args, **kwargs)

    return wrapped


def check_user_can_edit_team(f):
    """
    Decorator to check if the current user can edit the specified team.
    The team ID is expected to be provided in the request parameters.

    If the user does not have permission, an error response is returned.
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return error_response("User not authenticated", "unauthorized", 401)
        
        team_id = request.view_args.get('team_id') or request.args.get('team_id')
        if not team_id:
            return error_response("Team ID is required", "bad_request", 400)
        perms = get_team_management_permissions(team_id)
        if "CAN_EDIT_TEAM" not in perms:
            return error_response("User does not have permission to edit this team", "forbidden", 403)

        return f(*args, **kwargs)

    return wrapped


