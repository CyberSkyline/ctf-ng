from enum import Enum, auto
from dataclasses import dataclass, field

class PermissionEnum(str,Enum):
    CAN_EDIT_TEAM = "CAN_EDIT_TEAM"
    CAN_EDIT_USER = "CAN_EDIT_USER"
    CAN_MANAGE_SUPPORT_TICKETS = "CAN_MANAGE_SUPPORT_TICKETS"
    CAN_IMPERSONATE_USERS = "CAN_IMPERSONATE_USERS"
    CAN_VIEW_CHALLENGES = "CAN_VIEW_CHALLENGES"
    CAN_PLAY_CHALLENGES = "CAN_PLAY_CHALLENGES"
    CAN_START_TEAM_TIMER = "CAN_START_TEAM_TIMER"
    CAN_ACCESS_ADMIN_PANEL = "CAN_ACCESS_ADMIN_PANEL"
    CAN_LEAVE_TEAM = "CAN_LEAVE_TEAM"

class RoleEnum(str,Enum):
    ADMIN = "admin"
    SUPPORT = "support"


class DenyReason(Enum):
    NOT_AUTHENTICATED = auto()
    NOT_TEAM_MEMBER = auto()
    EVENT_LOCKED = auto()
    EVENT_ENDED = auto()
    EVENT_NOT_STARTED = auto()
    TEAM_NOT_STARTED = auto()
    TEAM_HAS_STARTED = auto()
    CAPTAIN_CANNOT_LEAVE = auto()
    MISSING_ROLE = auto()
    GENERIC = auto()
    TIME_LIMIT_EXCEEDED = auto()

@dataclass
class Denial:
    permission: PermissionEnum
    reason: DenyReason

@dataclass
class Grant:
    permission: PermissionEnum

@dataclass
class PermissionCheck:
    granted: list[Grant] = field(default_factory=list)
    denied: list[Denial] = field(default_factory=list)

    def add_grant(self, permission: PermissionEnum):
        self.granted.append(Grant(permission))

    def add_denial(self, permission: PermissionEnum, reason: DenyReason):
        self.denied.append(Denial(permission, reason))

    def merge(self, other: 'PermissionCheck'):
        self.granted.extend(other.granted)
        self.denied.extend(other.denied)