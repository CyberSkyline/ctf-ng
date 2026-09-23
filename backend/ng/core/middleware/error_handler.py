"""
Centralized error handling for the entire Flask application.
Provides a unified decorator and a global registration function.
"""

import logging
import traceback
from functools import wraps

from CTFd.models import db
from flask import current_app as app
from flask import request, session
from flask_limiter.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

from ..exceptions import APIException
from ..utils import error_response
from ..utils.logger import get_logger
from ..utils.sentry import error_scope

logger = get_logger(__name__)


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
            # The base class defaults to 500, so an APIException is not always
            # the caller's fault - and the ones that are not need reporting.
            # Those carry their traceback: the message is generic, so without
            # one the issue says a request failed but not where. A 4xx is the
            # caller's and needs no traceback in every rejected request's log.
            with error_scope(e.status_code):
                logger.log(
                    logging.ERROR if e.status_code >= 500 else logging.INFO,
                    "%s: %s",
                    e.__class__.__name__,
                    e.message,
                    extra={
                        "context": {
                            "status_code": e.status_code,
                            **_get_request_context(),
                        }
                    },
                    exc_info=e.status_code >= 500,
                )
            return error_response(
                e.message,
                e.error_field,
                e.status_code,
            )

        except IntegrityError as e:
            db.session.rollback()
            db.session.remove()
            with error_scope(500):
                logger.exception(
                    "Database integrity error",
                    extra={
                        "context": {
                            "error": str(e.orig) if hasattr(e, "orig") else str(e),
                            **_get_request_context(),
                        },
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
            with error_scope(500):
                logger.exception(
                    "Database error occurred",
                    extra={
                        "context": {
                            "error_type": type(e).__name__,
                            **_get_request_context(),
                        },
                    },
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
            with error_scope(500):
                logger.exception(
                    "Unexpected error: %s: %s",
                    type(e).__name__,
                    str(e),
                    extra={"context": _get_request_context()},
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
        with error_scope(error.status_code):
            logger.log(
                logging.ERROR if error.status_code >= 500 else logging.INFO,
                "%s: %s",
                error.__class__.__name__,
                error.message,
                extra={"context": {"status_code": error.status_code, **_get_request_context()}},
                # traceback on 5xx
                exc_info=error if error.status_code >= 500 else None,
            )
        return error_response(error.message, error.error_field, error.status_code)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        db.session.remove()
        # Reported as 500 to match the decorator: the response is a 409 the
        # caller can act on, but a write that violates a constraint is ours.
        # exc_info=error, not True: Flask calls this from inside its own except
        # block today, but sys.exc_info() is empty anywhere else.
        with error_scope(500):
            logger.error(
                "Database integrity error",
                extra={"context": _get_request_context()},
                exc_info=error,
            )
        return error_response("A resource with this name or value already exists.", "database", 409)

    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        db.session.rollback()
        db.session.remove()
        with error_scope(500):
            logger.error("SQLAlchemy error", extra={"context": _get_request_context()}, exc_info=error)
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

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_error(error):
        db.session.remove()
        return error_response("Rate limit reached for this operation", "rate_limit", 429)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        db.session.remove()
        # Werkzeug's own 4xx/5xx, not ours - reported as 500 (404 excluded above).
        with error_scope(500, werkzeug_status=error.code):
            logger.error(
                "Unhandled HTTP exception: %s %s",
                error.code,
                error.name,
                extra={"context": _get_request_context()},
                exc_info=error,
            )
        return error_response(
            error.description or error.name,
            "http_exception",
            error.code or 500,
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        db.session.remove()
        with error_scope(500):
            logger.error(
                "Unexpected error: %s",
                type(error).__name__,
                extra={"context": _get_request_context()},
                exc_info=error,
            )
        return error_response("An internal server error occurred.", "server", 500)

    logger.info("Global error handlers registered successfully.")