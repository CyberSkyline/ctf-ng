from flask_restx import Namespace, Resource
from ...core.utils.logger import get_logger
from ...core.utils.api import success_response
from ...core.middleware.auth import user_endpoint
from ...core.middleware.loaders.load_event import load_event
from ...core.middleware.loaders.load_team_by_user_and_event import load_team_by_user_and_event
from ...permissions.controllers.get_user_roles import get_user_roles
from ...core.middleware.loaders._util import LoaderType
from ...core.middleware.permission_middleware import (
    check_permissions,
)


permissions_user_namespace = Namespace("/permissions", description="Permissions management endpoints for users")
logger = get_logger(__name__)


@permissions_user_namespace.route("/<int:event_id>/me")
class UserPermissions(Resource):
    """
    Resource to get the current user's permissions.
    """
    @user_endpoint()
    @load_event(source=LoaderType.PARAM, output_key="event")
    @load_team_by_user_and_event(output_key="team")
    @check_permissions(None, "")
    @permissions_user_namespace.doc(
        description="Get the current user's permissions",
        responses={200: "Success", 401: "Unauthorized"},
    )
    def get(self, **kwargs):
        """
        Get the current user's permissions.
        """
        current_user = kwargs.get("current_user")
        permissions = kwargs.get("permissions", [])

        return success_response({
            "user_id": current_user.id,
            "permissions": permissions
        })

@permissions_user_namespace.route("/me")
class UserGlobalPermissions(Resource):
    """
    Resource to get the current user's global permissions.
    """
    @user_endpoint()
    @check_permissions(None, "")
    @permissions_user_namespace.doc(
        description="Get the current user's global permissions",
        responses={200: "Success", 401: "Unauthorized"},
    )
    def get(self, **kwargs):
        """
        Get the current user's global permissions.
        """
        current_user = kwargs.get("current_user")
        permissions = kwargs.get("permissions", [])

        return success_response({
            "user_id": current_user.id,
            "permissions": permissions
        })

@permissions_user_namespace.route("/me/roles")
class UserRoles(Resource):
    """
    Resource to get the current user's roles.
    """
    @user_endpoint()
    @permissions_user_namespace.doc(
        description="Get the current user's roles",
        responses={200: "Success", 401: "Unauthorized"},
    )
    def get(self, **kwargs):
        """
        Get the current user's roles.
        """
        current_user = kwargs.get("current_user")

        roles = get_user_roles(current_user.id)

        return success_response({
            "user_id": current_user.id,
            "roles": roles
        })