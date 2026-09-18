"""
Tests how Sentry is started, and which errors it is given.

The rule is that an issue is opened for a 5xx response or an uncaught
exception, and for nothing else - a handled 4xx stays a log line.
"""

import logging

import pytest
import sentry_sdk
from flask import session
from sentry_sdk.transport import Transport
from sentry_sdk.utils import event_from_exception, exc_info_from_error
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ...exceptions import APIException, NotFoundError
from ...middleware.error_handler import handle_exceptions
from ...utils.error_page import render_error_page
from ...utils.logger import PLUGIN_LOGGER_NAME, get_logger
from ...utils.sentry import (
    HTTP_STATUS_TAG,
    TRACES_SAMPLE_RATE,
    REDACTED,
    _release,
    _scrub_log,
    error_scope,
    init_sentry,
    install_event_processors,
    report_unexpected,
)


class _CapturingTransport(Transport):
    """Collects the events that survive the filter, in place of sending them."""

    def __init__(self):
        super().__init__()
        self.events = []
        self.logs = []
        self.item_types = []

    def capture_envelope(self, envelope):
        for item in envelope.items:
            self.item_types.append(item.headers.get("type"))
            if item.headers.get("type") == "event":
                self.events.append(item.payload.json)
            elif item.headers.get("type") == "log":
                self.logs.extend(item.payload.json.get("items", []))

    def flush(self, *args, **kwargs):
        pass

    def kill(self):
        pass


@pytest.fixture
def sentry(sentry_transport):
    """The events that survived the filter, for the common case."""
    return sentry_transport.events


@pytest.fixture
def sentry_transport():
    """A live Sentry client whose envelopes are captured instead of sent."""
    install_event_processors()

    transport = _CapturingTransport()
    sentry_sdk.init(
        dsn="https://key@example.ingest.sentry.io/1",
        transport=transport,
        traces_sample_rate=0,
        enable_logs=True,
        before_send_log=_scrub_log,
    )

    plugin_logger = logging.getLogger(PLUGIN_LOGGER_NAME)
    original_level = plugin_logger.level
    plugin_logger.setLevel(logging.DEBUG)

    yield transport

    plugin_logger.setLevel(original_level)
    sentry_sdk.get_global_scope().set_client(None)


def statuses(events):
    return [(event.get("tags") or {}).get(HTTP_STATUS_TAG) for event in events]


class TestSentryErrorFilter:
    def test_handled_4xx_does_not_open_an_issue(self, app, sentry):
        @handle_exceptions
        def raise_not_found():
            raise NotFoundError("Team not found")

        with app.test_request_context("/ng/teams/999"):
            raise_not_found()

        assert sentry == []

    def test_integrity_conflict_opens_an_issue(self, app, sentry):
        """
        A write that violates a constraint answers 409, so the caller can act
        on it, but is reported as 500 - getting there is our bug, not theirs.
        """
        @handle_exceptions
        def raise_conflict():
            raise IntegrityError("INSERT ...", {}, Exception("duplicate key"))

        with app.test_request_context("/ng/teams", method="POST"):
            _, status = raise_conflict()

        assert status == 409
        assert statuses(sentry) == [500]

    def test_unexpected_exception_opens_an_issue(self, app, sentry):
        @handle_exceptions
        def raise_unexpected():
            raise RuntimeError("Something broke badly")

        with app.test_request_context("/ng/scoring/submit", method="POST"):
            _, status = raise_unexpected()

        assert status == 500
        assert statuses(sentry) == [500]

    def test_database_error_opens_an_issue(self, app, sentry):
        @handle_exceptions
        def raise_database_error():
            raise SQLAlchemyError("connection gone")

        with app.test_request_context("/ng/scoring/submit", method="POST"):
            _, status = raise_database_error()

        assert status == 500
        assert statuses(sentry) == [500]

    def test_api_exception_defaulting_to_500_opens_an_issue(self, app, sentry):
        """The base class defaults to 500, so it is not always a caller error."""
        @handle_exceptions
        def raise_bare_api_exception():
            raise APIException("Something went wrong on our side")

        with app.test_request_context("/ng/teams"):
            _, status = raise_bare_api_exception()

        assert status == 500
        assert statuses(sentry) == [500]

    def test_a_500_api_exception_says_where_it_came_from(self, app, sentry):
        """
        Its message is generic, and Sentry groups an issue with no exception on
        the message template - which every APIException shares. The traceback
        is what makes one of these issues distinguishable from another.
        """
        @handle_exceptions
        def raise_bare_api_exception():
            raise APIException("Something went wrong on our side")

        with app.test_request_context("/ng/teams"):
            raise_bare_api_exception()

        frames = sentry[0]["exception"]["values"][0]["stacktrace"]["frames"]
        assert frames[-1]["function"] == "raise_bare_api_exception"

    def test_logged_error_outside_an_error_path_does_not_open_an_issue(self, sentry):
        """An error logged by a service that recovered, e.g. an S3 lookup."""
        get_logger("service").error("Error searching files: %s", "timeout")

        assert sentry == []

    def test_uncaught_exception_opens_an_issue_without_a_status(self, sentry):
        """What the Flask and WSGI integrations report when nothing caught it."""
        event, hint = event_from_exception(
            exc_info_from_error(RuntimeError("escaped the app")),
            mechanism={"type": "wsgi", "handled": False},
        )
        sentry_sdk.capture_event(event, hint=hint)

        assert len(sentry) == 1
        assert (sentry[0].get("tags") or {}).get(HTTP_STATUS_TAG) is None

    def test_error_scope_tags_do_not_leak(self, sentry):
        with error_scope(500):
            get_logger("service").error("Server failed")
        get_logger("service").error("A later, unrelated error")

        assert statuses(sentry) == [500]

    def test_report_unexpected_opens_an_issue_with_a_traceback(self, sentry):
        """The entry point a swallowed `except Exception` is meant to call."""
        logger = get_logger("service")

        try:
            raise RuntimeError("S3 said no")
        except RuntimeError as e:
            report_unexpected(logger, "Upload failed: %s", e)

        assert statuses(sentry) == [500]
        assert sentry[0]["exception"]["values"][0]["type"] == "RuntimeError"

    def test_report_unexpected_reports_500_even_if_the_response_is_a_4xx(self, sentry):
        """
        An `except Exception` with nothing more specific to say does not know
        whose fault this is, so it is never a clean 4xx just because that is
        what the caller goes on to answer with.
        """
        logger = get_logger("service")

        try:
            raise RuntimeError("S3 said no")
        except RuntimeError as e:
            report_unexpected(logger, "Upload failed: %s", e)
            # the caller then answers the request with e.g. a 400 ValidationError

        assert statuses(sentry) == [500]

    def test_report_unexpected_without_an_exception_still_opens_an_issue(self, sentry):
        """An `if not result: ...` failure, with nothing to attach a trace to."""
        logger = get_logger("service")

        report_unexpected(logger, "S3 not configured", exc_info=False)

        assert statuses(sentry) == [500]
        assert "exception" not in sentry[0]

    def test_report_unexpected_context_is_scrubbed(self, sentry):
        logger = get_logger("service")

        report_unexpected(logger, "Upload failed", exc_info=False, email="person@agency.gov")

        assert sentry[0]["extra"]["context"]["email"] == REDACTED

    def test_a_4xx_error_page_is_logged_without_opening_an_issue(self, app, sentry_transport):
        """
        WARNING is deliberate: high enough to outlive production's LOG_LEVEL,
        low enough to stay under the logging integration's event level.
        """
        with app.test_request_context("/ng/authenticate/okta/callback"):
            render_error_page("sso_state_mismatch", status=400)
        sentry_sdk.flush()

        assert sentry_transport.events == []
        assert [log["body"] for log in sentry_transport.logs] == [
            "Rendering error page: sso_state_mismatch"
        ]

    def test_an_unrouted_http_exception_opens_an_issue_with_a_traceback(self, app, sentry):
        """
        Werkzeug answers a method it does not recognize for the route on its
        own, before any of our exception types get a say - nothing anticipated
        it, so unlike a deliberate 4xx it is reported, and with a stack trace.

        Driven through `handle_user_exception`, the same entry point Flask
        itself calls from `full_dispatch_request`, rather than a real request
        to a real route: the app fixture is session-scoped and past the point
        new routes can be registered.
        """
        from werkzeug.exceptions import MethodNotAllowed

        with app.test_request_context("/ng/teams/999", method="PATCH"):
            response = app.handle_user_exception(MethodNotAllowed(["GET"]))

        assert response[1] == 405
        assert statuses(sentry) == [500]
        assert sentry[0]["tags"]["werkzeug_status"] == 405
        assert sentry[0]["exception"]["values"][0]["type"] == "MethodNotAllowed"

    def test_a_rate_limited_request_does_not_open_an_issue(self, app, sentry):
        """Rate limiting working as intended is not a failure to report."""
        from unittest.mock import Mock

        from flask_limiter.errors import RateLimitExceeded

        with app.test_request_context("/ng/teams"):
            response = app.handle_user_exception(RateLimitExceeded(Mock(error_message=None)))

        assert response[1] == 429

    def test_a_dropped_issue_is_still_logged_to_sentry(self, app, sentry_transport):
        """The filter removes issues, not the log stream they came from."""
        @handle_exceptions
        def raise_not_found():
            raise NotFoundError("Team not found")

        with app.test_request_context("/ng/teams/999"):
            raise_not_found()
        sentry_sdk.flush()

        assert sentry_transport.events == []
        assert [log["body"] for log in sentry_transport.logs] == ["NotFoundError: Team not found"]


@pytest.fixture
def clean_sentry_env(monkeypatch):
    """A process with nothing configured, plus teardown of any client started."""
    for name in (
        "SENTRY_DSN",
        "SENTRY_ENVIRONMENT",
        "SENTRY_RELEASE",
        "ENVIRONMENT",
        "STATIC_BUILD_PATH",
    ):
        monkeypatch.delenv(name, raising=False)

    yield monkeypatch

    sentry_sdk.get_global_scope().set_client(None)


def options():
    return sentry_sdk.get_client().options


class TestInitSentry:
    def test_no_dsn_leaves_sentry_off(self, clean_sentry_env):
        init_sentry(debug=False)

        assert not sentry_sdk.get_client().is_active()

    def test_placeholder_dsn_leaves_sentry_off(self, clean_sentry_env):
        """Both .env defaults ship SENTRY_DSN=- to mean "not configured"."""
        clean_sentry_env.setenv("SENTRY_DSN", "-")

        init_sentry(debug=False)

        assert not sentry_sdk.get_client().is_active()

    def test_deployment_supplies_environment_and_release(self, clean_sentry_env):
        sha = "a" * 40
        clean_sentry_env.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")
        clean_sentry_env.setenv("ENVIRONMENT", "PRODUCTION")
        clean_sentry_env.setenv("STATIC_BUILD_PATH", f"/dist/{sha}")

        init_sentry(debug=False)

        assert options()["environment"] == "production"
        assert options()["release"] == sha

    def test_staging_is_its_own_environment(self, clean_sentry_env):
        clean_sentry_env.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")
        clean_sentry_env.setenv("ENVIRONMENT", "staging")

        init_sentry(debug=False)

        assert options()["environment"] == "staging"

    def test_debug_is_its_own_environment(self, clean_sentry_env):
        clean_sentry_env.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")

        init_sentry(debug=True)

        assert options()["environment"] == "development"

    @pytest.mark.parametrize("debug", [True, False])
    def test_every_environment_traces_every_request(self, clean_sentry_env, debug):
        """Tracing is not sampled - the issue filter never judges a transaction."""
        clean_sentry_env.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")

        init_sentry(debug=debug)

        assert options()["traces_sample_rate"] == TRACES_SAMPLE_RATE == 1.0

    @pytest.mark.parametrize(
        ("static_build_path", "expected"),
        [
            (f"/dist/{'a' * 40}", "a" * 40),
            ("/static/", None),  # development, which names no build
            ("/dist/", None),
            ("", None),
        ],
    )
    def test_the_release_is_the_commit_the_assets_were_built_from(
        self,
        clean_sentry_env,
        static_build_path,
        expected,
    ):
        clean_sentry_env.setenv("STATIC_BUILD_PATH", static_build_path)

        assert _release() == expected

    def test_the_environment_can_override_what_is_derived(self, clean_sentry_env):
        clean_sentry_env.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")
        clean_sentry_env.setenv("ENVIRONMENT", "PRODUCTION")
        clean_sentry_env.setenv("SENTRY_ENVIRONMENT", "load-test")
        clean_sentry_env.setenv("SENTRY_RELEASE", "hand-rolled-build")

        init_sentry(debug=False)

        assert options()["environment"] == "load-test"
        assert options()["release"] == "hand-rolled-build"


class TestPiiScrubbing:
    def test_an_email_in_context_does_not_reach_an_issue(self, app, sentry):
        with app.test_request_context("/ng/authenticate/okta/callback"):
            with error_scope(500):
                get_logger("sso").error(
                    "Unexpected error during OAuth at stage %s",
                    "user_lookup",
                    extra={
                        "context": {
                            "failure_stage": "user_lookup",
                            "email": "person@agency.gov",
                            "oauth_id": "00u1a2b3c4",
                        }
                    },
                )

        context = sentry[0]["extra"]["context"]
        assert context["email"] == REDACTED
        assert context["oauth_id"] == REDACTED
        assert context["failure_stage"] == "user_lookup"

    def test_an_email_in_context_does_not_reach_a_log(self, app, sentry_transport):
        """Logs bypass event processors, so they are scrubbed separately."""
        with app.test_request_context("/ng/authenticate/okta/callback"):
            get_logger("sso").error(
                "Rendering error page: %s",
                "sso_state_mismatch",
                extra={"context": {"email": "person@agency.gov", "status_code": 400}},
            )
        sentry_sdk.flush()

        # The SDK renders a non-scalar attribute as a string for the envelope,
        # so the scrub has to have happened before it got here.
        context = sentry_transport.logs[0]["attributes"]["context"]["value"]
        assert "person@agency.gov" not in context
        assert REDACTED in context
        assert "'status_code': 400" in context

    def test_nested_and_listed_values_are_scrubbed_too(self, sentry):
        with error_scope(500):
            get_logger("sso").error(
                "Upstream rejected the token",
                extra={
                    "context": {
                        "accounts": [{"email": "person@agency.gov", "role": "admin"}],
                        "upstream": {"token": "eyJhbGci"},
                    }
                },
            )

        context = sentry[0]["extra"]["context"]
        assert context["accounts"] == [{"email": REDACTED, "role": "admin"}]
        assert context["upstream"] == {"token": REDACTED}

    def test_the_signed_in_user_is_identified_by_id_alone(self, app, sentry):
        with app.test_request_context("/ng/scoring/submit", method="POST"):
            session["id"] = 4821
            with error_scope(500):
                get_logger("scoring").error("Server failed")

        assert sentry[0]["user"] == {"id": 4821}

    def test_an_anonymous_request_reports_no_user(self, app, sentry):
        with app.test_request_context("/ng/scoring/submit", method="POST"):
            with error_scope(500):
                get_logger("scoring").error("Server failed")

        assert "user" not in sentry[0]

    def test_the_sdk_is_told_not_to_collect_pii_itself(self, clean_sentry_env):
        clean_sentry_env.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")

        init_sentry(debug=False)

        assert options()["send_default_pii"] is False

    def test_logs_are_scrubbed_on_their_way_out(self, clean_sentry_env):
        """Events go through a processor; logs need this hook instead."""
        clean_sentry_env.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")

        init_sentry(debug=False)

        assert options()["before_send_log"] is _scrub_log


class TestTracing:
    def test_the_filter_leaves_transactions_alone(self, clean_sentry_env):
        """Only errors are issues - judging a transaction by status drops it."""
        install_event_processors()
        transport = _CapturingTransport()
        clean_sentry_env.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")
        sentry_sdk.init(
            dsn="https://key@example.ingest.sentry.io/1",
            transport=transport,
            traces_sample_rate=1.0,
        )

        with sentry_sdk.start_transaction(name="GET /ng/scoring/leaderboard", op="http.server"):
            pass
        sentry_sdk.flush()

        assert "transaction" in transport.item_types
