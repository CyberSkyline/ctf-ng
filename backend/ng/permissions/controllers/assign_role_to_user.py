
from ...user.models.User import User
from ..models.Role import Role
from ..models.UserRole import UserRole
def assign_role_to_user(user_id, role_name):
    """
    Assign a role to a user.

    :param user_id: The ID of the user to assign the role to.
    :param role_name: The name of the role to assign.
    :return: The assigned role object.
    """
    user = User.query.get(user_id)
    if not user:
        return {"success": False, "error": f"User with ID {user_id} does not exist"}

    role = Role.query.filter_by(name=role_name).first()

    if not role:
        return {"success": False, "error": f"Role '{role_name}' does not exist"}

    UserRole.assign_role_to_user_by_id(user_id, role.id)

    return role