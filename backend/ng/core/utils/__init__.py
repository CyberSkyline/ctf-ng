from datetime import UTC, datetime
from .api import (
    error_response,
    serialize_model_for_api,
    success_response,
)
from .logger import (
    get_logger,
    logger,
)

def utc_now() -> datetime:
    """
    Get current UTC datetime
    Replacement for deprecated datetime.utcnow()
    """
    return datetime.now(UTC).replace(tzinfo=UTC)


def get_models():
    """Lazy import of models to avoid SQLAlchemy table creation during import."""
    from ...challenge.models import Challenge, ChallengeTag, ContainerBlueprint, Hint, Question
    from ...event.models import Demographic, Event
    from ...notifications.models import Notification
    from ...announcements.models import Announcement
    from ...permissions.models import Permission, Role, RolePermission, UserRole
    from ...scoring.models import Attempt, HintRedemption, ManualPointAward, Score, ScoreEvent
    from ...support.models import Ticket, TicketMessage, TicketTag, TicketAttachment
    from ...team.models import Team, TeamMember
    from ...user.models import User
    from ...sponsors.models.Sponsor import Sponsor
    from ...containers.models.IndvidualContainer import IndvidualContainer
    from ...containers.models.ContainerInstance import ContainerInstance
    from ..models.FileUpload import FileUpload
    from ...feedback.models import Feedback

    return {
        "Announcement": Announcement,
        "Attempt": Attempt,
        "Challenge": Challenge,
        "ChallengeTag": ChallengeTag,
        "ContainerBlueprint": ContainerBlueprint,
        "Demographic": Demographic,
        "Event": Event,
        "Feedback": Feedback,
        "FileUpload": FileUpload,
        "Hint": Hint,
        "HintRedemption": HintRedemption,
        "ManualPointAward": ManualPointAward,
        "Notification": Notification,
        "Permission": Permission,
        "Question": Question,
        "Role": Role,
        "RolePermission": RolePermission,
        "Score": Score,
        "ScoreEvent": ScoreEvent,
        "Team": Team,
        "TeamMember": TeamMember,
        "Ticket": Ticket,
        "TicketAttachment": TicketAttachment,
        "TicketMessage": TicketMessage,
        "TicketTag": TicketTag,
        "User": User,
        "Sponsor": Sponsor,
        "UserRole": UserRole,
        "ContainerInstance": ContainerInstance,
        "IndvidualContainer": IndvidualContainer,
    }


__all__ = [
    "get_logger",
    "logger",
    "utc_now",
    "serialize_model_for_api",
    "success_response",
    "error_response",
]
