from .create_permission import create_permission
from .create_role import create_role
from ..models.enums import PermissionEnum, RoleEnum
from ..models.Permission import Permission
from ..models.Role import Role
from ..models.RolePermission import RolePermission
from ..controllers.assign_role_to_user import assign_role_to_user


def initial_admin_setup(admin_user: "User" = None) -> None:
    """Perform the initial setup for the admin user, including creating permissions and roles."""
    create_permission(
        name=PermissionEnum.CAN_EDIT_TEAM,
        description="Can edit teams",
    )
    create_permission(
        name=PermissionEnum.CAN_EDIT_USER,
        description="Can edit users",
    )
    create_permission(
        name=PermissionEnum.CAN_MANAGE_SUPPORT_TICKETS,
        description="Can manage support tickets",
    )
    create_permission(
        name=PermissionEnum.CAN_IMPERSONATE_USERS,
        description="Can impersonate other users",
    )
    create_permission(
        name=PermissionEnum.CAN_VIEW_CHALLENGES,
        description="Can view challenges",
    )
    create_permission(
        name=PermissionEnum.CAN_PLAY_CHALLENGES,
        description="Can play challenges",
    )
    create_permission(
        name=PermissionEnum.CAN_START_TEAM_TIMER,
        description="Can start the team timer",
    )

    create_permission(
        name=PermissionEnum.CAN_ACCESS_ADMIN_PANEL,
        description="Can access the admin panel",
    )

    create_role(
        name=RoleEnum.ADMIN,
        permissions=[
            PermissionEnum.CAN_EDIT_TEAM,
            PermissionEnum.CAN_EDIT_USER,
            PermissionEnum.CAN_MANAGE_SUPPORT_TICKETS,
            PermissionEnum.CAN_IMPERSONATE_USERS,
            PermissionEnum.CAN_VIEW_CHALLENGES,
            PermissionEnum.CAN_PLAY_CHALLENGES,
            PermissionEnum.CAN_START_TEAM_TIMER,
            PermissionEnum.CAN_ACCESS_ADMIN_PANEL,
        ],
    )
    create_role(
        name=RoleEnum.SUPPORT,
        permissions=[
            PermissionEnum.CAN_MANAGE_SUPPORT_TICKETS,
            PermissionEnum.CAN_VIEW_CHALLENGES,
            PermissionEnum.CAN_ACCESS_ADMIN_PANEL,
        ],
    )
    if admin_user:
        assign_role_to_user(admin_user.id, RoleEnum.ADMIN)