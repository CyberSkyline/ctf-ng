from ..models.Permission import Permission


def create_permission(name, description):
    """Create a new permission."""
    if Permission.get_permission_by_name(name):
        return {"success": False, "error": f"Permission '{name}' already exists"}, 400

    permission = Permission.create_permission(name, description)
    if not permission:
        return {"success": False, "error": "Failed to create permission"}, 400
    return permission