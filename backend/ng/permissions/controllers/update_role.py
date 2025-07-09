from CTFd.models import db
from ..models.Role import Role
from ..models.Permission import Permission
from ..models.enums import PermissionEnum


def update_role(role_id, data):
    """
    Update the details of a specific role by ID.
    
    Args:
        role_id (int): The ID of the role to update.
        data (dict): The new data for the role, including name and permissions.
    
    Returns:
        dict: The updated role details or an error message.
    """

    role = Role.query.get(role_id)
    if not role:
        return {"error": "Role not found"}, 404

    role.name = data.get("name", role.name)
    permission_names = data.get("permissions", [])
    permissions = []
    if permission_names:
        for name in permission_names:
            try:
                permission = Permission.get_permission_by_name(PermissionEnum(name))
            except ValueError:
                return {
                    "success": False,
                    "error": f"Permission '{name}' does not exist",
                }
    role.permissions = permissions
    db.session.commit()

    return {
        "success": True,
        "role": role,
    }
