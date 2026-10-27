from sqlalchemy.orm import lazyload

from ..models.UserRole import UserRole
from ..models.Permission import Permission
from ..models.RolePermission import RolePermission
from ..models.enums import PermissionCheck

def get_user_permissions(user):
    """Get all Role based permissions for a specific user.

    Args:
        user (User): The user object.

    Returns:
        PermissionCheck: An object containing permission grants and denials.
    """
    trace = PermissionCheck()

    # load every permission across the user's roles in one query, rather than one query per permission
    permissions = (Permission.query
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .filter(UserRole.user_id == user.id)
        .options(lazyload(Permission.roles))
        .distinct()
        .all()
    )

    for permission in permissions:
        trace.add_grant(permission)

    return trace
