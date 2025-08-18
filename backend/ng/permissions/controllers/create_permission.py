from ..models.Permission import Permission


def create_permission(name, description):
    """Create a new permission."""
    if Permission.get_permission_by_name(name):
        raise ValueError(f"Permission '{name}' already exists")

    permission = Permission.create_permission(name, description)
    if not permission:
        raise ValueError("Failed to create permission")
    return permission