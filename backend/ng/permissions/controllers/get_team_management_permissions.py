from ...team.models.TeamMember import TeamMember
from ...team.models.enums import TeamRole
from ..models.Permission import Permission
from ..models.enums import PermissionEnum
from datetime import datetime
from ..models.enums import PermissionEnum, PermissionCheck, DenyReason

def get_team_management_permissions(team,user) -> PermissionCheck:

    """
    Get permissions for managing a team based on the current user's role in the team.
    """
    trace = PermissionCheck()
    team_member = TeamMember.find_by_user_and_team(user.id, team.id)
    if team_member is None:
        trace.add_denial(PermissionEnum.CAN_EDIT_TEAM, DenyReason.NOT_TEAM_MEMBER)
        return trace
    if team.event.locked:
        trace.add_denial(PermissionEnum.CAN_EDIT_TEAM, DenyReason.EVENT_LOCKED)
        return trace
    if team.event.end_time is not None and team.event.end_time < datetime.now():
        trace.add_denial(PermissionEnum.CAN_EDIT_TEAM, DenyReason.EVENT_ENDED)
        return trace
    if team.start_timestamp is not None:
        trace.add_denial(PermissionEnum.CAN_EDIT_TEAM, DenyReason.TEAM_HAS_STARTED)
        return trace
    if team_member.role == TeamRole.CAPTAIN:
        trace.add_grant(PermissionEnum.CAN_EDIT_TEAM)

    return trace


