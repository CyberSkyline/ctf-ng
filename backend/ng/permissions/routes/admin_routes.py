from flask_restx import Namespace, Resource
from ...core.utils.logger import get_logger
from ...core.utils.api import error_response, success_response
from ...core.middleware.auth import user_endpoint, admin_endpoint
from ..models.Role import Role
from ..models.UserRole import UserRole
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
    )
    def get(self, role_id, **kwargs):
        """
        Get all details for a specific role by ID.
        """
        role = Role.find_by_id(role_id)

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
        params={
            "json_data": {
                "description": "JSON data of updated role",
                "in": "body",
                "required": True,
                "example": {
                    "name": "new_role_name",
                    "description": "Updated description for the role"
                }
            }
        }
    )
    def put(self, role_id, **kwargs):
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
    @admin_endpoint()
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
        description="Update roles for a specific user by ID",
        responses={
            404: "User not found",
            200: "Success",
            400: "Bad Request - Invalid data",
            500: "Internal Server Error - Could not update user roles",
            403: "Forbidden - User does not have permission to update roles"
        },
        params={
            "json_data": {
                "description": "JSON data of updated roles",
                "in": "body",
                "required": True,
                "example": {
                    "roles": ["admin", "support"]
                }
            }
        }
    )
    def put(self, user_id, **kwargs):
        """
        Update roles for a specific user by ID.
        """
        data = kwargs.get("validated_data")
        if not data or "roles" not in data:
            return error_response("No role names provided", "roles", 400)

        user = UserRole.update_user_roles(user_id, data)

        return success_response(user)
