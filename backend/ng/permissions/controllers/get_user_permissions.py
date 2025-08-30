from ..models.UserRole import UserRole
from ..models.Role import Role
from ..models.enums import PermissionCheck

def get_user_permissions(user):
    """Get all Role based permissions for a specific user.

    Args:
        user (User): The user object.

    Returns:
        PermissionCheck: An object containing permission grants and denials.
    """
    trace = PermissionCheck()
    user_roles = UserRole.get_user_roles(user.id)
    permissions = []

    for role in user_roles:
        role_permissions = Role.get_permissions(role.id)
        permissions.extend(role_permissions)

    for permission in set(permissions):
        trace.add_grant(permission)

    return trace