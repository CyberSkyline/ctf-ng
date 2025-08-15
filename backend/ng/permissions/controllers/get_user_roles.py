from ...user.models.User import User
from ...permissions.models.UserRole import UserRole
from ...permissions.models.enums import RoleEnum
from CTFd.utils.user import get_current_user

def get_user_roles():
    """
    Get the current user's role.
    """

    user = get_current_user()
    if not user:
        return []
    ng_user = User.find_or_create_by_ctfd_id(user.id, commit=False)
    roles = UserRole.get_user_roles(ng_user.id)
    return [RoleEnum(role.name) for role in roles] if roles else []