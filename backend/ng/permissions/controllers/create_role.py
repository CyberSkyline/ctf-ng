from ..models.Role import Role
from ..models.Permission import Permission
def create_role(name: str, permissions: list[str] = None):
    """Create a new role with optional permissions.

    Args:
        name (str): Name of the role
        permissions (list[str], optional): List of permission names to assign to the role

    Returns:
        Role: The created role instance
        
    """

    if Role.get_role_by_name(name):
        return {"success": False, "error": f"Role '{name}' already exists"}

    permissions_obj = []
    if permissions:
        for perm_name in permissions:
            permission = Permission.get_permission_by_name(perm_name)
            if not permission:
                return {"success": False, "error": f"Permission '{perm_name}' does not exist"}
            permissions_obj.append(permission)

    return {"success": True, "role": Role.create_role(name=name, permissions=permissions_obj)}