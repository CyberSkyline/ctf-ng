#!/usr/bin/env python3
# Main Entry Point

from .routes import delete_unwanted_ctfd_routes, api_blueprint
from .routes.views import plugin_views
from .utils.logger import get_logger
from CTFd.models import db
from typing import Tuple, Any

logger = get_logger(__name__)


def _create_tables() -> Tuple[Any, Any, Any, Any]:
    from .event.models.Event import Event
    from .team.models.Team import Team
    from .user.models.User import User
    from .team.models.TeamMember import TeamMember
    from .event_registration.models.EventRegistration import EventRegistration

    return (
        Event,
        EventRegistration,
        Team,
        User,
        TeamMember,
    )


def load(app: Any) -> None:
    try:
        delete_unwanted_ctfd_routes(app)

        logger.info("Loading plugin", extra={"context": {"stage": "initialization"}})

        _create_tables()
        db.create_all()

        app.register_blueprint(plugin_views)
        app.register_blueprint(api_blueprint, url_prefix="/plugin/api")
        logger.info(
            "Plugin loaded successfully",
            extra={
                "context": {
                    "stage": "completed",
                    "blueprints": ["plugin_views", "api_blueprint"],
                }
            },
        )
    except (ImportError, AttributeError, TypeError) as e:
        logger.error(
            "Error with imports or configuration during plugin load",
            extra={"context": {"error": str(e), "stage": "failed_initialization"}},
        )
    except Exception as e:
        # Broad catch needed for unknown plugin initialization errors
        logger.error(
            "Unknown error loading plugin",
            extra={"context": {"error": str(e), "stage": "failed_initialization"}},
        )
