from ..models.UserRole import UserRole
from ..models.Role import Role

def update_user_roles(user_id, data):
    """
    Update roles for a specific user by ID.
    
    :param user_id: ID of the user to update roles for.
    :param data: Dictionary containing role IDs to assign to the user.
    :return: Response dictionary with success status and message.
    """
    role_names = data.get("roles", [])

    if not role_names:
        return {
            "success": False,
            "message": "No role names provided"
        }, 400

    for role_name in role_names:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return {
                "success": False,
                "error": f"Role '{role_name}' does not exist"
            }
    user_roles = UserRole.update_user_roles(user_id, role_names)
    

    return {
        "success": True,
        "message": "User roles updated successfully",
        "roles": user_roles
    }