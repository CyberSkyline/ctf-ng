"""
Centralized error handling for the entire Flask application.
Provides a unified decorator and a global registration function.
"""

from functools import wraps
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from CTFd.models import db

from ..exceptions import APIException
from ..utils import error_response
from ..utils.logger import get_logger

logger = get_logger(__name__)


def handle_exceptions(f):
    """
    A unified decorator that catches all application exceptions and ensures proper
    database session cleanup. Provides centralized logging and consistent JSON responses.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except APIException as e:  # 1. Predictable application errors first
            db.session.remove()
            logger.warning(
                f"Business Logic Error: {e.__class__.__name__}: {str(e)}",
                extra={
                    "context": {
                        "status_code": e.status_code,
                        "error_field": e.error_field,
                    }
                },
            )
            return error_response(e.message, e.error_field, e.status_code)

        except IntegrityError as e:  # 2. Database integrity violations
            db.session.rollback()
            db.session.remove()
            logger.error(
                "Database Integrity Error: A constraint was violated.",
                extra={"context": {"error": str(e.orig) if hasattr(e, "orig") else str(e)}},
                exc_info=True,
            )
            return error_response(
                "A resource with this name or value already exists.",
                "database_conflict",
                409,
            )

        except SQLAlchemyError as e:  # 3. Any other, more generic database error
            db.session.rollback()
            db.session.remove()
            logger.error(
                "Database error occurred.",
                extra={"context": {"error_type": type(e).__name__}},
                exc_info=True,
            )
            return error_response(
                "A database error occurred. Please contact an administrator.",
                "database_error",
                500,
            )

        except Exception as e:
            db.session.remove()
            import traceback

            print(f"ERROR: {str(e)}")
            print(traceback.format_exc())
            logger.exception("Unexpected internal server error occurred.")
            return error_response("An internal server error occurred.", "server_error", 500)

    return decorated_function


# --- The Global Registration Function  --- #
def register_error_handlers(app):
    """
    Registers global error handlers as a fallback safety net.
    """

    @app.errorhandler(APIException)
    def handle_api_error(error):
        db.session.remove()
        logger.warning(f"API Error: {error.__class__.__name__}: {str(error)}")
        return error_response(error.message, error.error_field, error.status_code)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        db.session.remove()
        logger.error("Database Integrity Error", exc_info=True)
        return error_response("A resource with this name or value already exists.", "database", 409)

    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        db.session.rollback()
        db.session.remove()
        logger.error("SQLAlchemy error occurred", exc_info=True)
        return error_response(
            "A database error occurred. Please contact an administrator.",
            "database",
            500,
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        db.session.remove()
        import traceback

        print(f"ERROR: {str(error)}")
        print(traceback.format_exc())
        logger.exception("Unexpected internal server error occurred")
        return error_response("An internal server error occurred.", "server", 500)

    logger.info("Global error handlers registered successfully.")
