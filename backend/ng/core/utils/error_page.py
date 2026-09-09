"""
Renders browser-facing failures as the frontend error page.

Most plugin routes are called by the SPA over fetch, so a JSON body from
`error_response` is the right answer. A handful of routes are loaded directly
in the browser instead - OAuth callbacks, external redirects - and there a JSON
body leaves the user staring at raw text. These serve the app itself with the
failure attached, so it renders with the rest of the app's chrome.
"""

import logging
from uuid import uuid4

from flask import Response
from flask import current_app as app

from .frontend import render_frontend
from .logger import get_logger
from .sentry import error_scope

logger = get_logger(__name__)


def render_error_page(
    code: str,
    *,
    status: int = 500,
    log_message: str | None = None,
    log_args: tuple[object, ...] = (),
    context: dict | None = None,
    detail: str | None = None,
    exc_info: bool = False,
) -> Response:
    """
    Log a browser-facing failure and render the frontend error page for it.

    The failure travels in the document, as `window.init.error`, rather than in
    the query string. Nothing about it is readable or editable in the URL, so a
    hand-crafted link cannot be used to put a chosen error in front of a victim,
    and the debug detail below is not exposed by a shared or logged URL.

    Args:
        code: Stable identifier for the failure. Must have a matching entry in
            the frontend's ERRORS map, or the page falls back to generic copy.
        status: HTTP status for the response, also shown on the page.
        log_message: Line to log, as a %-style template. Defaults to a
            description of the failure. Values belong in `log_args`, not in the
            template: Sentry groups non-exception events on the template, so a
            value baked into it opens a separate issue per value.
        log_args: Arguments for the `log_message` template.
        context: Extra structured fields to attach to the log entry.
        detail: Internal specifics (exception text, validation failure). Shown
            on the page only when the app is in debug mode, always logged.
        exc_info: Attach the active exception's traceback to the log entry.

    Returns:
        An HTML response carrying the frontend app and the failure to display.
        Returned as a `Response` so Flask-RESTX serves it as-is instead of
        encoding the document as JSON.
    """
    reference = uuid4().hex[:12]

    if log_message is None:
        log_message, log_args = "Rendering error page: %s", (code,)

    # Sentry does not index `extra`, so the reference the user is shown is only
    # searchable once it is a tag - which is the point of surfacing it at all.
    # The status decides the level. 5xx is ours, and logs at ERROR, which is
    # also what opens the Sentry issue. Below that the failure is the caller's
    # and opens nothing, but it still logs at WARNING rather than INFO: these
    # pages are the browser-facing failures a user reports by reference, and
    # production runs at LOG_LEVEL=WARNING, where an INFO line is dropped
    # before it reaches a handler - or Sentry's log stream.
    with error_scope(status, error_reference=reference, error_code=code):
        logger.log(
            logging.ERROR if status >= 500 else logging.WARNING,
            log_message,
            *log_args,
            extra={
                "context": {
                    "error_code": code,
                    "status_code": status,
                    "reference": reference,
                    **({"detail": detail} if detail else {}),
                    **(context or {}),
                },
            },
            exc_info=exc_info,
        )

    error = {"code": code, "status": status, "reference": reference}

    # `detail` can carry internal specifics, so it stays out of production pages.
    if detail and app.debug:
        error["detail"] = detail

    return Response(render_frontend(error=error), status=status, mimetype="text/html")
