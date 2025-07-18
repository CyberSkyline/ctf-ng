from ..models.UserRole import UserRole
from ..models.Role import Role


def get_user_permissions(user):
    """Get all permissions for a specific user.

    Args:
        user (User): The user object.

    Returns:
        list: A list of permissions assigned to the user.
    """
    user_roles = UserRole.get_user_roles(user.id)
    permissions = []

    for role in user_roles:
        role_permissions = Role.get_permissions(role.id)
        permissions.extend(role_permissions)

    return {
        "success": True,
        "permissions": list(set(permissions))
    }