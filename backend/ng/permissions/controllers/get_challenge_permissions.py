from ..models.enums import PermissionEnum
from datetime import datetime
from ...event.models.Event import Event
from ...team.models.Team import Team


def get_challenge_permissions(team: Team) -> list[str]:
    """Get all challenge-related permissions for a specific user in a team.

    Args:
        team (Team): The team instance.
        user (User): The user instance.

    Returns:
        list[str]: A list of permission strings.
    """
    permissions = []

    event = Event.find_by_id(team.event_id)
    if event.start_time is None or event.start_time < datetime.utcnow():
        if team.start_timestamp is not None:
            permissions.append(PermissionEnum.CAN_VIEW_CHALLENGES)
            if event.end_time is None or event.end_time > datetime.utcnow():
                permissions.append(PermissionEnum.CAN_PLAY_CHALLENGES)

    return permissions
