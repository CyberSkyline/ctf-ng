"""
Get users filtered by their roles - part of the permissions system.
"""

from ...core.exceptions import ValidationError

from ..models.Role import Role
from ..models.enums import RoleEnum
from ...user.models.User import User


def get_users_with_roles(role_names: list[str]) -> list[User]:
    """
    Get all users who have any of the specified roles
    """
    users = set()

    for role_name in role_names:
        try:
            role_enum = RoleEnum(role_name.lower())
        except ValueError:
            valid_roles = [role.value for role in RoleEnum]
            raise ValidationError(
                    f"Invalid role '{role_name}'. Valid roles are: {', '.join(valid_roles)}"
                    ) from None

        role_users = Role.get_users_with_role(role_enum)
        users.update(role_users)

    return list(users)


def get_support_role_users() -> list[User]:
    """
    Get all users who can be assigned support tickets
    """
    return get_users_with_roles(
            [RoleEnum.ADMIN.value,
             RoleEnum.SUPPORT.value]
            )
