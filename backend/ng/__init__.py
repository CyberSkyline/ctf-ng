#!/usr/bin/env python3

from typing import Any
from flask_socketio import SocketIO

from CTFd.models import db
from .core.utils.logger import get_logger
from .core.routes import delete_unwanted_ctfd_routes, api_blueprint
from .core.routes.views import plugin_views
from .core.middleware.error_handler import register_error_handlers
from .support import sockets as support_sockets
# from .notifications import sockets as notification_sockets

from .event.models.Event import Event  # noqa: F401
from .team.models.Team import Team  # noqa: F401
from .user.models.User import User  # noqa: F401
from .team.models.TeamMember import TeamMember  # noqa: F401
from .support.models.Ticket import Ticket  # noqa: F401
from .support.models.TicketMessage import TicketMessage  # noqa: F401
from .support.models.TicketTag import TicketTag  # noqa: F401
from .event.models.Demographic import Demographic  # noqa: F401
from .challenge.models.Challenge import Challenge  # noqa: F401
from .challenge.models.ContainerBlueprint import ContainerBlueprint  # noqa: F401
from .challenge.models.Hint import Hint  # noqa: F401
from .challenge.models.Question import Question  # noqa: F401
from .challenge.models.ChallengeTag import ChallengeTag # noqa: F401
from .scoring.models.Score import Score  # noqa: F401
from .scoring.models.ScoreEvent import ScoreEvent  # noqa: F401
from .scoring.models.Attempt import Attempt  # noqa: F401
from .scoring.models.HintRedemption import HintRedemption  # noqa: F401
from .scoring.models.ManualPointAward import ManualPointAward  # noqa: F401
from .notifications.models.Notification import Notification  # noqa: F401

logger = get_logger(__name__)


def load(app: Any) -> None:
    try:
        delete_unwanted_ctfd_routes(app)

        logger.info("Loading plugin", extra={"context": {"stage": "initialization"}})

        db.create_all()

        register_error_handlers(app)

        # Will be ignored for now
        socketio = SocketIO(
            app,
            async_mode="gevent",
            message_queue=app.config.get("REDIS_URL"),
            cors_allowed_origins="*",
        )

        app.extensions["socketio"] = socketio

        support_sockets.initialize_socket_handlers(socketio)
        # notification_sockets.initialize_notification_sockets(socketio)

        app.register_blueprint(plugin_views)
        app.register_blueprint(api_blueprint, url_prefix="/ng")
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
