"""
Removes a member from a team with captain handling.
"""

# from ...core import BusinessLogicError
# from ..models.TeamMember import TeamMember
# from ..models.enums import TeamRole


def remove_member(team_id: int, member_to_remove_id: int, actor_id: int, is_admin: bool = False) -> None:
    """Removes a member from a team with auth checks.
    Returns:
        dict: Operation result data
    """
    raise Exception("Not implemented yet")
    # team = g.team
    # event = g.event
    # team_member_to_remove = g.target_member

    # if not is_admin:

    #     if team.locked:
    #         raise BusinessLogicError(f"Team '{team.name}' is locked and members cannot be removed")

    # if team_member_to_remove.user_id == actor_id:
    #     raise BusinessLogicError("Captains cannot remove themselves. Use the 'Leave Team' or 'Disband Team' feature.")

    # if team_member_to_remove.role == TeamRole.CAPTAIN:
    #     return _handle_captain_removal(team, team_member_to_remove, actor_id, is_admin)

    # team.remove_member_and_regenerate_code(team_member_to_remove.id)

    # return {
    #     "member_removed": True,
    #     "member_id": team_member_to_remove.user_id,
    #     "was_captain": False,
    # }


# def _handle_captain_removal(team, captain_to_remove: TeamMember, actor_id: int, is_admin: bool) -> dict[str, Any]:
#     """Handles captain removal by either auto promoting or blocking."""
#     remaining_members = TeamMember.find_remaining_members_for_captain_removal(team.id, captain_to_remove.id)

#     if not remaining_members:
#         captain_to_remove.remove_team_member()
#         return {
#             "captain_removed": True,
#             "captain_id": captain_to_remove.user_id,
#             "team_now_empty": True,
#             "new_captain_promoted": False,
#         }

#     if is_admin:
#         new_captain = remaining_members[0]
#         team.remove_captain_and_promote(
#             captain_to_remove_id=captain_to_remove.id,
#             new_captain_user_id=new_captain.user_id,
#         )

#         return {
#             "captain_removed": True,
#             "captain_id": captain_to_remove.user_id,
#             "new_captain_promoted": True,
#             "new_captain_id": new_captain.user_id,
#             "team_now_empty": False,
#         }
#     else:
#         raise BusinessLogicError(
#             "You cannot remove the captain while other members are on the team. Please transfer captaincy first."
#         )
