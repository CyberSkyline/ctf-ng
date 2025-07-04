from enum import Enum

class Permissions_Types(Enum):
    """
    Enum representing different permissions
    """

    CAN_EDIT_TEAM = "can_edit_team"
    CAN_EDIT_USER = "can_edit_user"
    CAN_MANAGE_SUPPORT_TICKETS = "can_manage_support_tickets"

    def __str__(self):
        return self.value