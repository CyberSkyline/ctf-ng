from flask_restx import Namespace, Resource
from ...core.utils.logger import get_logger
from ...core.utils.api import error_response, success_response
from ...core.middleware.auth import user_endpoint, admin_endpoint
from ..models.Role import Role
from ..models.UserRole import UserRole
from ..controllers import get_role_details
from ...core.middleware.loaders.load_role import load_role
from ...core.middleware.loaders.load_user import load_user
from ...core.middleware.loaders._util import LoaderType


permissions_admin_namespace = Namespace("/admin/permissions", description="Permissions management endpoints for admins")
logger = get_logger(__name__)


@permissions_admin_namespace.route("/<int:role_id>/details")
class RoleDetails(Resource):
    """
    Resource to manage permissions for a specific role.
    """
    @admin_endpoint()
    @permissions_admin_namespace.doc(
        description="Get all details for a specific role by ID",
        responses={404: "Role not found", 200: "Success"},
        params={"role_id": "Role ID to retrieve details for"},
    )
    def get(self, role_id):
        """
        Get all details for a specific role by ID.
        """
        role_details = get_role_details(role_id)
        if not role_details.get("success"):
            return error_response(role_details.get("error", "Role not found"), "role", 404)
        role = role_details.get("role")
        return success_response(role)

    @admin_endpoint(
        json_required=True,
        validation_func=Role.validate_role_update
    )
    @load_role(source=LoaderType.PARAM, output_key="role")
    @permissions_admin_namespace.doc(
        description="Update the details of a specific role by ID",
        responses={
            404: "Role not found", 
            200: "Success",
            400: "Bad Request - Invalid data",
            500: "Internal Server Error - Could not update role",
            403: "Forbidden - User does not have permission to update role"

        },
        params={"role_id": "Role ID to update"},
        body={
            "name": "Name of the role",
            "description": "Description of the role",
            "permissions": "List of permission names to assign to the role"
        }
    )
    def patch(self, role_id, **kwargs):
        """
        Update the details of a specific role by ID.
        """
        data = kwargs.get("validated_data")
        if not data:
            return error_response("No data provided", "data", 400)

        role = Role.update_role(kwargs.get("role"), data)
        return success_response(role)


@permissions_admin_namespace.route("/<int:user_id>/roles")
class UserRoles(Resource):
    """
    Resource to manage roles for a specific user.
    """
    @user_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="user")
    @permissions_admin_namespace.doc("get_user_roles")
    def get(self, user_id, **kwargs):
        """
        Get all roles for a specific user by ID.
        """

        roles = UserRole.get_user_roles(user_id)
        return success_response(roles)

    @admin_endpoint(
        json_required=True,
        validation_func=UserRole.validate_user_role_update
    )
    @load_user(source=LoaderType.PARAM, output_key="user")
    @permissions_admin_namespace.doc(
        description="Update roles for a specific user by Name",
        responses={
            404: "User not found",
            200: "Success",
            400: "Bad Request - Invalid data",
            500: "Internal Server Error - Could not update user roles",
            403: "Forbidden - User does not have permission to update roles"
        },
        params={"user_id": "User ID to update roles for"},
        body={
            "role_ids": "List of role names to assign to the user"
        }
    )
    def patch(self, user_id, **kwargs):
        """
        Update roles for a specific user by ID.
        """
        data = kwargs.get("validated_data")
        if not data or "roles" not in data:
            return error_response("No role names provided", "roles", 400)

        user = UserRole.update_user_roles(user_id, data)

        return success_response(user)
