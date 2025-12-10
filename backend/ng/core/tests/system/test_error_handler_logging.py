"""
Tests for error handler logging behavior
"""

import logging
import pytest

from ...exceptions import (
    NotFoundError,
    ValidationError,
    BusinessLogicError,
)
from ...middleware.error_handler import (
    handle_exceptions,
    _get_request_context,
)
from ...utils.logger import PLUGIN_LOGGER_NAME


@pytest.fixture
def enable_logging(caplog):
    """
    Enable log propagation for caplog to capture logs during tests
    """
    plugin_logger = logging.getLogger(PLUGIN_LOGGER_NAME)
    error_handler_logger = logging.getLogger(
        f"{PLUGIN_LOGGER_NAME}.ng.core.middleware.error_handler"
    )

    original_propagate = plugin_logger.propagate
    original_level = plugin_logger.level

    plugin_logger.propagate = True
    plugin_logger.setLevel(logging.DEBUG)
    error_handler_logger.propagate = True
    error_handler_logger.setLevel(logging.DEBUG)

    yield

    plugin_logger.propagate = original_propagate
    plugin_logger.setLevel(original_level)
    error_handler_logger.propagate = original_propagate


class TestErrorHandlerLogging:
    """
    Tests that errors are logged at correct levels with proper context
    """
    def test_api_exception_logs_at_info_level(self, app, caplog, enable_logging):
        """
        4XX errors should log at INFO, not WARNING
        """
        @handle_exceptions
        def raise_not_found():
            raise NotFoundError("Team not found")

        with app.test_request_context("/ng/teams/999", method = "GET"):
            with caplog.at_level(logging.DEBUG, logger = PLUGIN_LOGGER_NAME):
                response, status = raise_not_found()

        assert status == 404

        info_logs = [r for r in caplog.records if r.levelno == logging.INFO]
        warning_logs = [r for r in caplog.records if r.levelno == logging.WARNING]

        assert len(info_logs) >= 1
        assert len(warning_logs) == 0

        log_record = info_logs[-1]
        assert "NotFoundError" in log_record.message
        assert "Team not found" in log_record.message

    def test_validation_error_logs_at_info_level(
        self,
        app,
        caplog,
        enable_logging
    ):
        """
        ValidationError (400) should log at INFO
        """
        @handle_exceptions
        def raise_validation():
            raise ValidationError(
                "Invalid input",
                errors = {"name": "Name is required"}
            )

        with app.test_request_context("/ng/teams", method = "POST"):
            with caplog.at_level(logging.DEBUG, logger = PLUGIN_LOGGER_NAME):
                response, status = raise_validation()

        assert status == 400

        info_logs = [r for r in caplog.records if r.levelno == logging.INFO]
        assert len(info_logs) >= 1
        assert "ValidationError" in info_logs[-1].message

    def test_business_logic_error_logs_at_info_level(
        self,
        app,
        caplog,
        enable_logging
    ):
        """
        BusinessLogicError (400) should log at INFO
        """
        @handle_exceptions
        def raise_business_error():
            raise BusinessLogicError("Cannot leave team as captain")

        with app.test_request_context("/ng/teams/1/leave", method = "POST"):
            with caplog.at_level(logging.DEBUG, logger = PLUGIN_LOGGER_NAME):
                response, status = raise_business_error()

        assert status == 400

        info_logs = [r for r in caplog.records if r.levelno == logging.INFO]
        assert len(info_logs) >= 1
        assert "BusinessLogicError" in info_logs[-1].message

    def test_unexpected_exception_logs_at_error_level(
        self,
        app,
        caplog,
        enable_logging
    ):
        """
        5XX errors should log at ERROR with stack trace
        """
        @handle_exceptions
        def raise_unexpected():
            raise RuntimeError("Something broke badly")

        with app.test_request_context("/ng/scoring/submit", method = "POST"):
            with caplog.at_level(logging.DEBUG, logger = PLUGIN_LOGGER_NAME):
                response, status = raise_unexpected()

        assert status == 500

        error_logs = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_logs) >= 1

        log_record = error_logs[-1]
        assert "RuntimeError" in log_record.message
        assert log_record.exc_info is not None

    def test_log_includes_request_path_and_method(
        self,
        app,
        caplog,
        enable_logging
    ):
        """
        Log entries should include request path and method
        """
        @handle_exceptions
        def raise_error():
            raise NotFoundError("Not found")

        with app.test_request_context("/ng/events/123/teams", method = "GET"):
            with caplog.at_level(logging.DEBUG, logger = PLUGIN_LOGGER_NAME):
                raise_error()

        info_logs = [r for r in caplog.records if r.levelno == logging.INFO]
        assert len(info_logs) >= 1

        log_record = info_logs[-1]
        context = log_record.context

        assert context["path"] == "/ng/events/123/teams"
        assert context["method"] == "GET"

    def test_4xx_does_not_include_stack_trace(self, app, caplog, enable_logging):
        """
        4XX errors should NOT include stack traces (exc_info)
        """
        @handle_exceptions
        def raise_not_found():
            raise NotFoundError("Resource missing")

        with app.test_request_context("/ng/test", method = "GET"):
            with caplog.at_level(logging.DEBUG, logger = PLUGIN_LOGGER_NAME):
                raise_not_found()

        info_logs = [r for r in caplog.records if r.levelno == logging.INFO]
        assert len(info_logs) >= 1

        log_record = info_logs[-1]
        assert log_record.exc_info is None

    def test_5xx_includes_stack_trace(self, app, caplog, enable_logging):
        """
        5XX errors SHOULD include stack traces
        """
        @handle_exceptions
        def raise_server_error():
            raise Exception("Unexpected failure")

        with app.test_request_context("/ng/test", method = "POST"):
            with caplog.at_level(logging.DEBUG, logger = PLUGIN_LOGGER_NAME):
                raise_server_error()

        error_logs = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_logs) >= 1

        log_record = error_logs[-1]
        assert log_record.exc_info is not None


class TestRequestContextHelper:
    """
    Tests for the _get_request_context helper
    """
    def test_returns_path_and_method_in_request_context(self, app):
        """
        Should return path and method when in request context
        """
        with app.test_request_context("/ng/teams/5", method = "DELETE"):
            context = _get_request_context()

        assert context["path"] == "/ng/teams/5"
        assert context["method"] == "DELETE"

    def test_returns_empty_dict_outside_request_context(self):
        """
        Should return empty dict when outside request context
        """
        context = _get_request_context()
        assert context == {}
