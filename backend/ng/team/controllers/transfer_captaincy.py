"""
Transfers captain role from current captain to another member.
"""

# from ..models.TeamMember import TeamMember


def transfer_captaincy(team_id: int, new_captain_id: int, actor_id: int, is_admin: bool = False) -> None:
    """Transfers captain role from current captain to another member.

    Returns:
        dict: Success status and updated team objects
    """
    raise Exception("This function is not implemented yet.")
    # team = g.team
    # new_captain_team_member = g.target_member

    # existing_captain = TeamMember.find_captain_by_team(team.id)

    # TeamMember.transfer_captain_role(
    #     team_id=team.id,
    #     old_captain_id=existing_captain.id if existing_captain else None,
    #     new_captain_id=new_captain_team_member.id,
    # )


