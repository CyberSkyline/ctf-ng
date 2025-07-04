
from ..models.permissions_enum import Permissions_Types
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
        raise ValueError("User not found")

    role = Role.query.filter_by(name=role_name).first()

    if not role:
        raise ValueError(f"Role '{role_name}' does not exist")

    UserRole.assign_role_to_user_by_id(user_id, role.id)