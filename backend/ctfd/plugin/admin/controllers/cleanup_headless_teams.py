"""
/plugin/admin/controllers/cleanup_headless_teams.py
Contains the business logic for an admin tool that finds and fixes teams without a captain.
"""

from CTFd.models import db
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...team.models.enums import TeamRole
from ...utils.logger import get_logger

logger = get_logger(__name__)


def cleanup_headless_teams():
    """Finds and fixes teams without a captain due to user deletion."""

    teams_with_members = (
        db.session.query(Team.id).join(TeamMember).group_by(Team.id).having(db.func.count(TeamMember.id) > 0).subquery()
    )
    teams_without_captain = (
        db.session.query(Team.id)
        .outerjoin(
            TeamMember,
            db.and_(Team.id == TeamMember.team_id, TeamMember.role == TeamRole.CAPTAIN),
        )
        .group_by(Team.id)
        .having(db.func.count(TeamMember.id) == 0)
        .subquery()
    )

    headless_team_ids = (
        db.session.query(teams_with_members.c.id)
        .join(teams_without_captain, teams_with_members.c.id == teams_without_captain.c.id)
        .all()
    )

    fixed_count = 0
    for (team_id,) in headless_team_ids:
        members = TeamMember.query.filter_by(team_id=team_id).order_by(TeamMember.joined_at.asc()).all()
        if members:
            # Promote the oldest member
            new_captain = members[0]
            new_captain.update_role(TeamRole.CAPTAIN)
            fixed_count += 1
            logger.warning(f"Fixed headless team {team_id} by promoting user {new_captain.user_id} to captain.")

    if fixed_count > 0:
        db.session.commit()

    return {
        "success": True,
        "message": f"Cleanup complete. Fixed {fixed_count} headless teams.",
    }
