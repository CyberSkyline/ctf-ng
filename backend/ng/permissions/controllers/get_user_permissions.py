from ..models.Permission import Permission
from ..models.enums import PermissionCheck

def get_user_permissions(user):
    """Get all Role based permissions for a specific user.

    Args:
        user (User): The user object.

    Returns:
        PermissionCheck: An object containing permission grants and denials.
    """
    trace = PermissionCheck()

    for permission in Permission.get_permissions_for_user(user.id):
        trace.add_grant(permission)

    return trace
