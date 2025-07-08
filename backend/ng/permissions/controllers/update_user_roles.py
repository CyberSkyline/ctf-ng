from ..models.UserRole import UserRole
from ..models.Role import Role
from ..models.enums import RoleEnum

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

    role_enums = []
    for role_name in role_names:
        try:
            role_enums.append(RoleEnum(role_name))
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid role name: {role_name}"
            }

    user_roles = UserRole.update_user_roles(user_id, role_enums)

    return {
        "success": True,
        "roles": user_roles
    }