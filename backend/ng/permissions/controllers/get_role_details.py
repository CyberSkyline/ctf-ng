from ...permissions.models.Role import Role

def get_role_details(role_id: int) -> dict:
    """
    Get all details for a specific role by ID.

    Args:
        role_id (int): ID of the role

    Returns:
        dict: Serialized role data including permissions
    """

    role = Role.query.get_or_404(role_id)
    if not role:
        return {"success": False, "error": "Role not found"}
    users = Role.get_users_with_role(role.name)
    return {"success": True, "role": role, "users": [user for user in users]}