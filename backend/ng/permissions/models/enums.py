from enum import Enum

class PermissionEnum(str,Enum):
    CAN_EDIT_TEAM = "can_edit_team"
    CAN_EDIT_USER = "can_edit_user"
    CAN_MANAGE_SUPPORT_TICKETS = "can_manage_support_tickets"

class RoleEnum(str,Enum):
    ADMIN = "admin"
    SUPPORT = "support"