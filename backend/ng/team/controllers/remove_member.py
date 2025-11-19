from ...team.models import TeamMember
from ...event.models import Demographic
from CTFd.models import db


def remove_member(team, user):
    """
    Remove a member from the team and regenerate the team's join code.
    """
    last_member = len(team.members) == 1
    user = user.ctfd_user if hasattr(user, "ctfd_user") else user
    team_member = TeamMember.find_by_user_and_team(user.id, team.id)
    team_member.remove_team_member(commit = False)

    demographic = Demographic.find_by_user_and_event(user.id, team.event_id)
    demographic.delete(commit = False)
    if last_member:
        team.disband_team(commit = False)

    db.session.commit()