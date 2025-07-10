from flask_restx import Namespace, Resource
from flask import g
from ...core.utils.logger import get_logger
from ...core.utils.api import error_response
from ...core.middleware.auth import api_endpoint, admin_endpoint
from ..models.Role import Role
from ...user.models.User import User
from ..models.UserRole import UserRole
from ..controllers import get_role_details, update_role, get_user_roles, update_user_roles


permissions_admin_namespace = Namespace("/admin/permissions", description="Permissions management endpoints for admins")
logger = get_logger(__name__)


6

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
        users = role_details.get("users", [])
        return {
            "success": True,
            "role": role.serialize(),
            "users": [user.serialize() for user in users],
        }

    @admin_endpoint(
        json_required=True,
        validation_func=Role.validate_role_update
    )
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
    def patch(self, role_id):
        """
        Update the details of a specific role by ID.
        """
        data = g.json_data
        if not data:
            return error_response("No data provided", "data", 400)

        role = Role.query.get_or_404(role_id)
        if not role:
            return error_response("Role not found", "role", 404)

        response = update_role(role_id, data)
        if "error" in response:
            return error_response(response["error"], "role", 400)
        return {
            "success": True,
            "role": response.get("role", {}).serialize(),
            "message": response.get("message", "Role updated successfully")
        }


@permissions_admin_namespace.route("/<int:user_id>/roles")
class UserRoles(Resource):
    """
    Resource to manage roles for a specific user.
    """
    @api_endpoint()
    @permissions_admin_namespace.doc("get_user_roles")
    def get(self, user_id):
        """
        Get all roles for a specific user by ID.
        """

        response = get_user_roles(user_id)
        roles = response.get("roles", [])
        return {
            "success": True,
            "roles": [role.serialize() for role in roles]
        }

    @admin_endpoint(
        json_required=True,
        validation_func=UserRole.validate_user_role_update
    )
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
    def patch(self, user_id):
        """
        Update roles for a specific user by ID.
        """
        data = g.json_data
        if not data or "roles" not in data:
            return error_response("No role names provided", "roles", 400)

        User.query.get_or_404(user_id)

        response = update_user_roles(user_id, data)
        if "error" in response:
            return error_response(response["error"], "user", 400)

        return {
            "success": True,
            "message": response.get("message", "User roles updated successfully"),
            "user": response.get("user").serialize(include_admin_fields=True),
        }
