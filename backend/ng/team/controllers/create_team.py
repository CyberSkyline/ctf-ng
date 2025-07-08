"""
Creates a new team in an event with the creator as captain.
"""

from ..models.Team import Team
# from ...core import BusinessLogicError
# from ...core.validation import (
#     validate_unique_name,
# )
# from ._generate_invite_code import _generate_invite_code


def create_team(name: str, ranked: bool = False) -> Team:
    """Creates a new team in the event with the creator as captain.

    Returns:
        Team: Created team instance
    """
    raise Exception("Not implemented yet")
    # event = g.event
    # user = g.user
    # eligibility = g.user_eligibility

    # if not eligibility["can_join"]:
    #     raise BusinessLogicError("You are already in a team for this event.")

    # validate_unique_name(Team, name, scope_field="event_id", scope_value=event.id)

    # invite_code = _generate_invite_code()

    # team = Team.create_team_with_captain(
    #     name=name,
    #     event_id=event.id,
    #     creator_id=user.id,
    #     invite_code=invite_code,
    #     ranked=ranked,
    # )

    # return team
