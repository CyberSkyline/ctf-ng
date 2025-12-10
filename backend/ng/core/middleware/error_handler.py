"""
Centralized error handling for the entire Flask application.
Provides a unified decorator and a global registration function.
"""

import traceback
from functools import wraps

from CTFd.models import db
from flask import current_app as app, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..exceptions import APIException
from ..utils import error_response
from ..utils.logger import get_logger

logger = get_logger(__name__)


def _get_request_context() -> dict:
    """
    Get basic request context for logging
    """
    try:
        return {
            "path": request.path,
            "method": request.method,
        }
    except RuntimeError:
        return {}


def handle_exceptions(f):
    """
    A unified decorator that catches all application exceptions and ensures proper
    database session cleanup. Provides centralized logging and consistent JSON responses.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except APIException as e:
            db.session.remove()
            logger.info(
                f"{e.__class__.__name__}: {e.message}",
                extra={
                    "context": {
                        "status_code": e.status_code,
                        **_get_request_context(),
                    }
                },
            )
            return error_response(
                e.message,
                e.error_field,
                e.status_code,
            )

        except IntegrityError as e:
            db.session.rollback()
            db.session.remove()
            logger.error(
                "Database integrity error",
                extra={
                    "context": {
                        "error": str(e.orig) if hasattr(e, "orig") else str(e),
                        **_get_request_context(),
                    }
                },
            )
            return error_response(
                "A resource with this name or value already exists.",
                "database_conflict",
                409,
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.remove()
            logger.error(
                "Database error occurred",
                extra={
                    "context": {
                        "error_type": type(e).__name__,
                        **_get_request_context(),
                    }
                },
                exc_info=True,
            )
            return error_response(
                traceback.format_exc() if app.debug else "A database error occurred.",
                "database_error",
                500,
            )

        except Exception as e:
            db.session.remove()
            logger.error(
                f"Unexpected error: {type(e).__name__}: {str(e)}",
                extra={
                    "context": _get_request_context(),
                },
                exc_info=True,
            )
            return error_response(
                traceback.format_exc() if app.debug else "An internal server error occurred.",
                "server_error",
                500,
            )

    return decorated_function


def register_error_handlers(app):
    """
    Registers global error handlers as a fallback safety net.
    """
    @app.errorhandler(APIException)
    def handle_api_error(error):
        db.session.remove()
        logger.info(
            f"{error.__class__.__name__}: {error.message}",
            extra={"context": {"status_code": error.status_code, **_get_request_context()}},
        )
        return error_response(error.message, error.error_field, error.status_code)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        db.session.remove()
        logger.error("Database integrity error", extra={"context": _get_request_context()})
        return error_response("A resource with this name or value already exists.", "database", 409)

    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        db.session.rollback()
        db.session.remove()
        logger.error("SQLAlchemy error", extra={"context": _get_request_context()}, exc_info=True)
        return error_response(
            "A database error occurred. Please contact an administrator.",
            "database",
            500,
        )

    @app.errorhandler(404)
    def handle_not_found_error(error):
        db.session.remove()
        logger.info("Route not found", extra={"context": _get_request_context()})
        return error_response("Resource not found.", "not_found", 404)

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        db.session.remove()
        logger.error(
            f"Unexpected error: {type(error).__name__}",
            extra={"context": _get_request_context()},
            exc_info=True,
        )
        return error_response("An internal server error occurred.", "server", 500)

    logger.info("Global error handlers registered successfully.")
