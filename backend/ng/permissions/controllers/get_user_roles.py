from ..models.UserRole import UserRole


def get_user_roles(user_id: int):
    """Get all roles for a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of roles assigned to the user.
    """
    user_roles = UserRole.get_user_roles(user_id)
    return {
        "success": True,
        "roles": user_roles
    }