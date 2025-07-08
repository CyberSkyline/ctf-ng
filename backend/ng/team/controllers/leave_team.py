"""
Removes a user from their current team in an event.
"""

# from ...core import BusinessLogicError
# from ..models.TeamMember import TeamMember
# from ..models.enums import TeamRole


def leave_team() -> None:
    """Removes a user from their current team in the event.

    Returns:
        dict: Confirmation message and former team name.
    """
    raise Exception("Not implemented yet")
    # team_member = g.team_member
    # team = g.team
    # event = g.event

    # if team.locked:
    #     raise BusinessLogicError(f"Team '{team.name}' is locked and members cannot leave")

    # if team_member.role == TeamRole.CAPTAIN:
    #     other_members_count = TeamMember.count_other_members_in_team(team.id, team_member.id)
    #     if other_members_count == 0:
    #         team_name = team.name
    #         team.disband_team()
    #         return {
    #             "team_disbanded": True,
    #             "team_name": team_name,
    #             "was_last_member": True,
    #         }

    # team_name = team.name
    # team_member.remove_team_member()

    # return {
    #     "left_team": True,
    #     "team_name": team_name,
    #     "team_disbanded": False,
    # }
