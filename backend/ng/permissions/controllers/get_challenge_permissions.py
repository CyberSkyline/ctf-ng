from ...event.models.Event import Event
from ...team.models.Team import Team
from ...core.utils import utc_now
from ..models.enums import PermissionEnum, PermissionCheck, DenyReason

def get_challenge_permissions(team: Team):
    """Get all challenge-related permissions for a specific user in a team.

    Args:
        team (Team): The team instance.
        user (User): The user instance.

    Returns:
        PermissionCheck: An object containing permission grants and denials.
    """
    trace = PermissionCheck()
    event = Event.find_by_id(team.event_id)
    now = utc_now()

    if event.start_time is not None and event.start_time > now:
        reason = DenyReason.EVENT_NOT_STARTED
        trace.add_denial(PermissionEnum.CAN_VIEW_CHALLENGES, reason)
        trace.add_denial(PermissionEnum.CAN_PLAY_CHALLENGES, reason)
        return trace

    if team.start_timestamp is None:
        reason = DenyReason.TEAM_NOT_STARTED
        trace.add_denial(PermissionEnum.CAN_VIEW_CHALLENGES, reason)
        trace.add_denial(PermissionEnum.CAN_PLAY_CHALLENGES, reason)
        return trace

    trace.add_grant(PermissionEnum.CAN_VIEW_CHALLENGES)

    if event.end_time is not None and event.end_time <= now:
        trace.add_denial(PermissionEnum.CAN_PLAY_CHALLENGES, DenyReason.EVENT_ENDED)
    else:
        trace.add_grant(PermissionEnum.CAN_PLAY_CHALLENGES)

    return trace