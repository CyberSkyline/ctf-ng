from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...team.models.enums import TeamRole
from ..models.Permission import Permission
from ...core.utils import get_current_user_id


def get_team_management_permissions(team_id):

    """
    Get permissions for managing a team based on the current user's role in the team.
    """

    permissions = []
    user_id = get_current_user_id()
    team = Team.find_by_id(team_id)
    if team is None:
        return {
            "success": False,
            "error": f"Team with ID {team_id} does not exist"
        }
    team_member = TeamMember.find_by_user_and_team(user_id, team_id)
    if team_member is None:
        return permissions
    if team_member.role == TeamRole.CAPTAIN:
        permissions.append(Permission.get_permission_by_name("CAN_EDIT_TEAM"))

    return {
        "success": True,
        "permissions": permissions
    }



    