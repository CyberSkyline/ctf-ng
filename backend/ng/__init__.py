#!/usr/bin/env python3

from typing import Any

from CTFd.models import db
from . import config
from .core.utils.logger import get_logger
from .core.routes import delete_unwanted_ctfd_routes, api_blueprint, remove_registered_helpers, remove_registered_errorhandlers
from .core.routes.views import plugin_views
from .core.middleware.error_handler import register_error_handlers
from .core.utils.redis_notifications import initialize_redis_notifications
from .notifications import sockets as notification_sockets
from .fileuploads import load as load_fileuploads
from flask_socketio import SocketIO

from .announcements.models.Announcement import Announcement  # noqa: F401
from .challenge.models.Challenge import Challenge  # noqa: F401
from .challenge.models.ChallengeTag import ChallengeTag  # noqa: F401
from .challenge.models.ContainerBlueprint import ContainerBlueprint  # noqa: F401
from .challenge.models.Hint import Hint  # noqa: F401
from .challenge.models.Question import Question  # noqa: F401
from .core.middleware.error_handler import register_error_handlers
from .core.models.FileUpload import FileUpload  # noqa: F401
from .core.routes import (
    api_blueprint,
    delete_unwanted_ctfd_routes,
    remove_registered_errorhandlers,
    remove_registered_helpers,
)
from .core.routes.views import plugin_views
from .core.utils.logger import get_logger
from .core.utils.rate_limit import limiter
from .core.utils.redis_notifications import initialize_redis_notifications
from .event.models.Demographic import Demographic  # noqa: F401
from .event.models.Event import Event  # noqa: F401
from .feedback.models.Feedback import Feedback  # noqa: F401
from .fileuploads import load as load_fileuploads
from .notifications import sockets as notification_sockets
from .notifications.models.Notification import Notification  # noqa: F401
from .scoring.models.Attempt import Attempt  # noqa: F401
from .scoring.models.HintRedemption import HintRedemption  # noqa: F401
from .scoring.models.ManualPointAward import ManualPointAward  # noqa: F401
from .scoring.models.Score import Score  # noqa: F401
from .scoring.models.ScoreEvent import ScoreEvent  # noqa: F401
from .support.models.Ticket import Ticket  # noqa: F401
from .support.models.TicketAttachment import TicketAttachment  # noqa: F401
from .support.models.TicketMessage import TicketMessage  # noqa: F401
from .support.models.TicketTag import TicketTag  # noqa: F401
from .team.models.Team import Team  # noqa: F401
from .team.models.TeamMember import TeamMember  # noqa: F401
from .user.models.User import User  # noqa: F401

logger = get_logger(__name__)


def load(app: Any) -> None:
    try:
        delete_unwanted_ctfd_routes(app)
        remove_registered_helpers(app)
        remove_registered_errorhandlers(app)

        logger.info("Loading plugin", extra={"context": {"stage": "initialization"}})

        app.config['MAX_CONTENT_LENGTH'] = config.MAX_REQUEST_SIZE

        db.create_all()

        register_error_handlers(app)

        socketio = SocketIO(
            app,
            message_queue=app.config.get("REDIS_URL"),
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True
        )

        notification_sockets.initialize_notification_sockets(socketio)

        app.extensions["socketio"] = socketio
        redis_manager = initialize_redis_notifications(socketio)
        if redis_manager:
            logger.info("Redis notification system initialized successfully")
        else:
            logger.warning("Redis notification system failed to initialize")

        app.config["RATELIMIT_STORAGE_URI"] = app.config.get("REDIS_URL")

        limiter.init_app(app)

        app.register_blueprint(plugin_views)
        app.register_blueprint(api_blueprint, url_prefix="/ng")

        # Load AWS configuration from environment
        import os
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY') and os.getenv('AWS_S3_BUCKET_NAME'):
            app.config['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
            app.config['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
            app.config['AWS_S3_BUCKET_NAME'] = os.getenv('AWS_S3_BUCKET_NAME')
            app.config['AWS_REGION'] = os.getenv('AWS_REGION', 'us-east-1')
            logger.info("AWS S3 configuration loaded from environment")
        else:
            logger.warning("AWS S3 environment variables not found - file operations will be disabled")

        # Initialize S3 service
        from .core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        s3_service.init_app(app)

        if s3_service.is_configured():
            logger.info("S3 service initialized successfully")
        else:
            logger.warning("S3 service not configured - file operations disabled")

        # Load fileuploads module
        load_fileuploads(app)

        logger.info(
            "Plugin loaded successfully",
            extra={
                "context": {
                    "stage": "completed",
                    "blueprints": ["plugin_views", "api_blueprint"],
                    "features": ["socketio", "redis_pubsub", "notifications", "fileuploads"],
                    "s3_configured": s3_service.is_configured()
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