"""
Centralized error handling for the entire Flask application.
Provides a unified decorator and a global registration function.
"""

import sys
import traceback
from functools import wraps

import sentry_sdk
from CTFd.models import db
from flask import current_app as app
from flask import request, session
from flask_limiter.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..exceptions import APIException
from ..utils import error_response
from ..utils.logger import get_logger

logger = get_logger(__name__)

def _get_small_traceback(limit = 3) -> str:
    exc_type, exc, tb = sys.exc_info()
    if tb is None:
        return ""

    frames = traceback.extract_tb(tb)

    # Most recent call first, limit frames
    frames = frames[-limit:][::-1]

    return ''.join(traceback.format_list(frames))


def _get_request_context() -> dict:
    """
    Get basic request context for logging
    """
    try:
        context = {
            "path": request.path,
            "method": request.method,
        }
        user_id = session.get("id")
        if user_id is not None:
            context["user_id"] = user_id
        return context
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
            sentry_sdk.capture_exception(e)
            logger.error(
                "Database integrity error",
                extra={
                    "context": {
                        "error": str(e.orig) if hasattr(e, "orig") else str(e),
                        **_get_request_context(),
                    },
                    "trace": _get_small_traceback()
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
            sentry_sdk.capture_exception(e)
            logger.error(
                "Database error occurred",
                extra={
                    "context": {
                        "error_type": type(e).__name__,
                        **_get_request_context(),
                    },
                    "trace": _get_small_traceback()
                },
                exc_info=True,
            )
            return error_response(
                traceback.format_exc() if app.debug else "A database error occurred.",
                "database_error",
                500,
            )

        except RateLimitExceeded:
            db.session.remove()
            return error_response("Rate limit reached for this operation", "rate_limit", 429)

        except Exception as e:
            db.session.remove()
            sentry_sdk.capture_exception(e)
            logger.error(
                f"Unexpected error: {type(e).__name__}: {str(e)}",
                extra={
                    "context": _get_request_context(),
                    "trace": _get_small_traceback(),
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
        sentry_sdk.capture_exception(error)
        logger.error("Database integrity error", extra={"context": _get_request_context()})
        return error_response("A resource with this name or value already exists.", "database", 409)

    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        db.session.rollback()
        db.session.remove()
        sentry_sdk.capture_exception(error)
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
        sentry_sdk.capture_exception(error)
        logger.error(
            f"Unexpected error: {type(error).__name__}",
            extra={"context": _get_request_context()},
            exc_info=True,
        )
        return error_response("An internal server error occurred.", "server", 500)

    logger.info("Global error handlers registered successfully.")