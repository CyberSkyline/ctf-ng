"""
Utility functions for common plugin functionality.
"""

from datetime import datetime, timezone

from .emitters import emit_event
from .logger import (
    get_logger,
    logger,
)
from .api import (
    success_response,
    error_response,
    serialize_model_for_api,
)
from .update import (
    build_update_data,
    build_conditional_update_data,
)

# --------Global utc function ----------#
def utc_now() -> datetime:
    """
    Get current UTC datetime
    Replacement for deprecated datetime.utcnow()
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

def get_models():
    """Lazy import of models to avoid SQLAlchemy table creation during import."""
    from ...user.models.User import User
    from ...team.models.Team import Team
    from ...event.models.Event import Event
    from ...support.models.Ticket import Ticket
    from ...team.models.TeamMember import TeamMember
    from ...support.models.TicketTag import TicketTag
    from ...event_registration.models.Demographic import Demographic
    from ...event_registration.models.EventRegistration import EventRegistration

    return {
        "User": User,
        "Team": Team,
        "Event": Event,
        "Ticket": Ticket,
        "TeamMember": TeamMember,
        "TicketTag": TicketTag,
        "Demographic": Demographic,
        "EventRegistration": EventRegistration,
    }

__all__ = [
    "get_logger",
    "logger",
    "utc_now",
    "serialize_model_for_api",
    "success_response",
    "error_response",
    "build_update_data",
    "build_conditional_update_data",
    "emit_event",
]
