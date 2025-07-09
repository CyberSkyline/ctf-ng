from enum import Enum

class PermissionEnum(str,Enum):
    CAN_EDIT_TEAM = "CAN_EDIT_TEAM"
    CAN_EDIT_USER = "CAN_EDIT_USER"
    CAN_MANAGE_SUPPORT_TICKETS = "CAN_MANAGE_SUPPORT_TICKETS"

class RoleEnum(str,Enum):
    ADMIN = "admin"
    SUPPORT = "support"