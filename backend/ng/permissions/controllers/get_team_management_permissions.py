from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...team.models.enums import TeamRole
from ..models.Permission import Permission
from ..models.enums import PermissionEnum
from datetime import datetime


def get_team_management_permissions(team,user):

    """
    Get permissions for managing a team based on the current user's role in the team.
    """

    permissions = []
    team_member = TeamMember.find_by_user_and_team(user.id, team.id)
    if team_member is None:
        return permissions
    if team.event.locked:
        return permissions
    if team.event.end_time is not None and team.event.end_time < datetime.now():
        return permissions
    if team.start_timestamp is not None:
        return permissions
    if team_member.role == TeamRole.CAPTAIN:
        permissions.append(Permission.get_permission_by_name(PermissionEnum.CAN_EDIT_TEAM))


    return permissions



