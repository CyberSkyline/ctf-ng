"""
Controller for sending challenge update announcements/notifications
"""

from ...team.models import TeamMember
from ...notifications.services import NotificationService


def notify_challenge_update(
    event_id: int,
    challenge_id: int,
    challenge_name: str,
    update_reason: str,
) -> dict:
    """
    Send challenge update announcements to all event participants

    Args:
        event_id: Event ID
        challenge_id: Challenge ID that was updated
        challenge_name: Name of the challenge
        update_reason: Description of what changed

    Returns:
        dict with announcement results
    """
    NotificationService.notify_challenge_updated(
        event_id=event_id,
        challenge_id=challenge_id,
        challenge_name=challenge_name,
        update_reason=update_reason,
    )

    participant_count = TeamMember.query.filter_by(event_id=event_id).count()

    return {
        "challenge_id": challenge_id,
        "challenge_name": challenge_name,
        "participants_notified": participant_count,
        "update_reason": update_reason,
    }
