#!/usr/bin/env python3

from .routes import delete_unwanted_ctfd_routes, api_blueprint
from .routes.views import plugin_views
from .utils.logger import get_logger
from CTFd.models import db
from typing import Tuple, Any

logger = get_logger(__name__)


def _create_tables() -> Tuple[Any, Any, Any, Any]:
    from .models.World import World
    from .models.Team import Team
    from .models.User import User
    from .models.TeamMember import TeamMember

    return (
        World,
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
    except Exception as e:
        logger.error(
            "Error loading plugin",
            extra={"context": {"error": str(e), "stage": "failed_initialization"}},
        )
