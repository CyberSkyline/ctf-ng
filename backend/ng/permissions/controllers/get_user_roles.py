from ...user.models.User import User
from ...permissions.models.enums import RoleEnum
from ...core.utils.current_user import get_current_user

def get_user_roles(user_id=None):
    """
    Get the roles for a user.
    """

    if user_id is None:
        current = get_current_user()
        user = User.find_or_create_by_ctfd_id(current.id) if current else None
    else:
        user = User.find_by_id(user_id)

    if not user:
        return []
    return [RoleEnum(role.name) for role in user.roles]
