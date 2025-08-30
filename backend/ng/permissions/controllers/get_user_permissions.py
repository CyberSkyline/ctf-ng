from ..models.UserRole import UserRole
from ..models.Role import Role
from ..models.enums import PermissionEnum, PermissionCheck, DenyReason

def get_user_permissions(user):
    """Get all Role based permissions for a specific user.

    Args:
        user (User): The user object.

    Returns:
        list: A list of permissions assigned to the user.
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