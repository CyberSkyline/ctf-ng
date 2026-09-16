"""
Starts Sentry, and decides which errors are worth an issue.

The SDK's logging integration turns every `logger.error` into an issue, whoever
logged it - this plugin, CTFd core, boto3, requests. Most of those errors are
handled ones: a rejected SSO callback, a file that is not there, an S3 lookup
that degrades to an empty list. They belong in the logs, and an issue for each
one buries the failures that actually need someone.

So an issue is created for the two cases that mean the server itself failed:

- the error path reports a 5xx, which it declares with `error_scope` - usually
  because that is what it answers, sometimes to own a failure it answers 4xx for
- the exception reached Sentry uncaught, carrying `mechanism.handled == False`
  (the Flask and WSGI integrations, and anything else that reports a crash)

Everything else is dropped on its way out. This applies to issues only.
Structured logs travel a different path in the SDK, so a dropped issue is still
a log line - the detail stays, the false alarms go.

How far down that stream reaches is LOG_LEVEL's call, not Sentry's. Production
runs at `WARNING`, and `logging` discards a record below the logger's level
before any handler or the SDK is asked about it. So a handled failure worth
reading afterwards is logged at `WARNING`: `INFO` reaches neither stdout nor
Sentry there, which is a quieter way of losing it than dropping the issue.

Both paths are scrubbed of the fields that identify a person, so a log call
that is correct today cannot carry an address into a third-party service after
someone adds a field to its context. Identity travels as a user id instead,
which is enough for Sentry to count how many people a failure reached.
"""

import logging
import os
from collections.abc import Iterator, Mapping
from contextlib import contextmanager

import sentry_sdk
from flask import has_request_context, session
from sentry_sdk.scope import Scope, add_global_event_processor

from .logger import get_logger

logger = get_logger(__name__)

# Tag naming the status an error path reports itself as. Usually the one the
# response answers with, but a path may report higher to say the failure is
# ours: an integrity conflict answers 409 and reports 500. Also the marker the
# filter below looks for, so an event without it is one no error path claimed.
HTTP_STATUS_TAG = "http_status"

# Every request is traced, in every environment. Performance data answers to
# this rate and nothing else: the issue filter leaves transactions alone, so a
# request reports its full span tree whether it answered 200, 404 or 500 - and
# a slow endpoint that fails is exactly the one worth having the spans for.
TRACES_SAMPLE_RATE = 1.0

# A git commit, as `.bin/update_commit_env.sh` writes it into STATIC_BUILD_PATH.
_SHA_LENGTH = 40

# Fields naming a person or granting access, redacted wherever they appear in an
# event or a log. The SSO paths are the ones that hold them today, but the point
# of scrubbing centrally is not to depend on knowing that.
PII_FIELDS = frozenset(
    {
        "email",
        "oauth_id",
        "password",
        "secret",
        "token",
        "authorization",
        "api_key",
    }
)

REDACTED = "[redacted]"

# Whether the processors below are registered. They are global to the process
# and appending them twice would run each event through them twice.
_installed = False


def init_sentry(*, debug: bool) -> None:
    """
    Start Sentry, if a DSN says where to send to.

    Called from the plugin's `load`, which is the one startup path every
    deployment shares - CTFd runs it from `create_app` under both the dev
    server and gunicorn. `SENTRY_ENVIRONMENT` and `SENTRY_RELEASE` are read by
    the SDK itself, so setting either in the environment overrides what is
    derived here.

    Args:
        debug: Whether the app is running in debug mode, which decides the
            environment name when the deploy has not set one.
    """
    dsn = os.environ.get("SENTRY_DSN", "").strip()

    # "-" is the placeholder both .env defaults ship, meaning "not configured".
    if not dsn or dsn == "-":
        logger.info("Sentry not configured, no DSN set")
        return

    options = {
        "dsn": dsn,
        "enable_logs": True,
        "traces_sample_rate": TRACES_SAMPLE_RATE,
        # Keeps the SDK from attaching request bodies, cookies and IPs of its
        # own accord. Off by default, set here so a reader can see the choice.
        "send_default_pii": False,
        # Events are scrubbed by an event processor, which logs do not run
        # through - this is the equivalent hook for them.
        "before_send_log": _scrub_log,
    }

    if "SENTRY_ENVIRONMENT" not in os.environ:
        options["environment"] = _environment(debug=debug)

    release = os.environ.get("SENTRY_RELEASE") or _release()
    if release:
        options["release"] = release

    sentry_sdk.init(**options)

    logger.info(
        "Sentry initialized",
        extra={
            "context": {
                "environment": options.get("environment"),
                "release": options.get("release"),
                "traces_sample_rate": options["traces_sample_rate"],
            }
        },
    )


def _environment(*, debug: bool) -> str:
    """Which deployment this is, so one Sentry project can hold them all."""
    # Set to PRODUCTION or staging by the deploy, and read by init_secrets.py to
    # pick which secret variants to use.
    environment = os.environ.get("ENVIRONMENT", "").strip().lower()

    return environment or ("development" if debug else "production")


def _release() -> str | None:
    """
    The deployed commit, or None when nothing recorded one.

    Taken from `STATIC_BUILD_PATH`, which the deploy points at `/dist/<sha>` -
    the same sha `frontend/vite.config.ts` bakes into the asset paths and
    reports as the frontend's release. Sharing it puts both halves of a deploy
    under one release in Sentry.
    """
    candidate = os.environ.get("STATIC_BUILD_PATH", "").strip().rstrip("/").rsplit("/", 1)[-1]

    if len(candidate) != _SHA_LENGTH or not all(c in "0123456789abcdef" for c in candidate):
        return None

    return candidate


@contextmanager
def error_scope(status: int, **tags: object) -> Iterator[Scope]:
    """
    Report the errors raised inside this block as a `status` failure.

    Anything Sentry captures in the block - an explicit `capture_exception`, or
    the event the logging integration builds from a `logger.error` - is tagged
    with the status, which is what decides whether it becomes an issue. The
    scope is local to the block, so the tags do not leak onto later events.

    The signed-in user's id is attached as well, so Sentry can report how many
    people an issue reached. The id alone: an address would say nothing further
    about the failure, and would put a real address in a third-party service.

    Args:
        status: Status to report this error as. The response's own status,
            unless the path means to say the failure is the server's.
        tags: Further tags to set, e.g. the reference shown to the user. A tag
            whose value is None is skipped rather than recorded as "None".

    Yields:
        The scope, for attaching anything else the event should carry.
    """
    with sentry_sdk.new_scope() as scope:
        scope.set_tag(HTTP_STATUS_TAG, status)
        for key, value in tags.items():
            if value is not None:
                scope.set_tag(key, value)

        user_id = _current_user_id()
        if user_id is not None:
            scope.set_user({"id": user_id})

        yield scope


def report_unexpected(
    logger: logging.Logger,
    message: str,
    *args: object,
    exc_info: bool | BaseException = True,
    **context: object,
) -> None:
    """
    Log and report a failure nothing anticipated - for an `except Exception`
    that will not re-raise (the central handler already reports one that
    does). Always reported as 500, whatever status the caller answers with.

    Args:
        logger: The module's own logger.
        message: A %-style template, not an f-string.
        args: The template's arguments.
        exc_info: True (default) from inside the except block, the exception
            itself if not, or False if there is none.
        context: Extra fields for the log, scrubbed like any other context.
    """
    with error_scope(500):
        logger.error(
            message,
            *args,
            extra={"context": context} if context else None,
            exc_info=exc_info,
        )


def _current_user_id() -> int | None:
    """The signed-in user's id, or None when anonymous or outside a request."""
    if not has_request_context():
        return None

    return session.get("id")


def _scrub(value: object) -> object:
    """Redact the PII fields anywhere within a structure of dicts and lists."""
    if isinstance(value, dict):
        return {
            key: REDACTED if _is_pii(key) else _scrub(item)
            for key, item in value.items()
        }

    if isinstance(value, list | tuple):
        return [_scrub(item) for item in value]

    return value


def _is_pii(key: object) -> bool:
    return isinstance(key, str) and key.lower() in PII_FIELDS


def _scrub_event(event: dict, hint: dict) -> dict:
    """Redact PII from where a log call's `extra` and the SDK's context land."""
    for section in ("extra", "contexts"):
        if event.get(section):
            event[section] = _scrub(event[section])

    return event


def _scrub_log(log: dict, hint: dict) -> dict:
    """
    Redact PII from a structured log's attributes.

    Attributes still hold their original Python values at this point - the
    SDK converts them to typed values later, when it builds the envelope.
    """
    if log.get("attributes"):
        log["attributes"] = _scrub(log["attributes"])

    return log


def _is_uncaught(event: dict) -> bool:
    """Whether the event reports an exception that nothing handled."""
    for exception in (event.get("exception") or {}).get("values") or []:
        mechanism = exception.get("mechanism")
        if isinstance(mechanism, Mapping) and mechanism.get("handled") is False:
            return True
    return False


def _server_errors_only(event: dict, hint: dict) -> dict | None:
    """Keep 5xx responses and uncaught exceptions; drop every other issue."""
    # Only errors are issues. Transactions and check-ins pass through the same
    # processors, and judging them by status would switch tracing off.
    if event.get("type") is not None:
        return event

    if _is_uncaught(event):
        return event

    status = (event.get("tags") or {}).get(HTTP_STATUS_TAG)
    if status is not None and str(status).startswith("5"):
        return event

    return None


def install_event_processors() -> None:
    """
    Scrub PII from issues and narrow them to server failures, process-wide.

    Registered as global processors rather than as a `before_send` at
    `sentry_sdk.init`, so that they hold for any client the process ends up
    with, and stay next to the code that raises the errors. Safe to call when
    Sentry is not configured: with no DSN nothing is captured and neither
    processor runs.
    """
    global _installed
    if _installed:
        return

    add_global_event_processor(_scrub_event)
    add_global_event_processor(_server_errors_only)
    _installed = True
