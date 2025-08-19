from ...user.models.User import User
from ...permissions.models.UserRole import UserRole
from ...permissions.models.enums import RoleEnum
from CTFd.utils.user import get_current_user

def get_user_roles(user_id=None):
    """
    Get the roles for a user.
    """
    
    user = get_current_user() if user_id is None else User.find_by_id(user_id)
    if not user:
        return []
    ng_user = User.find_or_create_by_ctfd_id(user.id, commit=True)
    roles = UserRole.get_user_roles(ng_user.id)
    return [RoleEnum(role.name) for role in roles] if roles else []