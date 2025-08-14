from ..models.Role import Role
from ..models.Permission import Permission
from ..models.enums import PermissionEnum
def create_role(name: str, permissions: list[PermissionEnum] = None):
    """Create a new role with optional permissions.

    Args:
        name (str): Name of the role
        permissions (list[PermissionEnum], optional): List of permission enums to assign to the role

    Returns:
        Role: The created role instance
    """

    if Role.get_role_by_name(name):
        raise ValueError(f"Role '{name}' already exists")
    permissions_obj = []
    if permissions:
        for perm_name in permissions:
            permission = Permission.get_permission_by_name(perm_name)
            if not permission:
                raise ValueError(f"Permission '{perm_name}' does not exist")
            permissions_obj.append(permission)

    return Role.create_role(name=name, permissions=permissions_obj)
