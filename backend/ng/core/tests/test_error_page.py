"""
Tests the levels the browser-facing error page logs at.

The level is what decides both whether Sentry opens an issue and whether the
line survives production's LOG_LEVEL, so the two ends of the range are pinned:
a 5xx is ours and logs at ERROR, and everything below it stays at WARNING.
"""

import json
import logging
import re

import pytest

from ..utils.error_page import render_error_page
from ..utils.logger import PLUGIN_LOGGER_NAME

WINDOW_INIT_ERROR = re.compile(r"error:\s*(\{.*?\}|null)\s*\n", re.DOTALL)


def levels(caplog):
    return {record.levelno for record in caplog.records}


@pytest.fixture
def rendered(app, caplog):
    """Render an error page, with the records it logged left in `caplog`."""
    # The plugin logger does not propagate under pytest, which is how caplog
    # sees a record at all.
    plugin_logger = logging.getLogger(PLUGIN_LOGGER_NAME)
    original_propagate = plugin_logger.propagate
    original_level = plugin_logger.level
    plugin_logger.propagate = True
    plugin_logger.setLevel(logging.DEBUG)

    def render(**kwargs):
        with app.test_request_context("/ng/authenticate/okta/callback"):
            with caplog.at_level(logging.DEBUG, logger=PLUGIN_LOGGER_NAME):
                return render_error_page(**kwargs)

    yield render

    plugin_logger.propagate = original_propagate
    plugin_logger.setLevel(original_level)


class TestErrorPageLogLevel:
    def test_a_4xx_logs_at_warning(self, rendered, caplog):
        """
        Production runs at LOG_LEVEL=WARNING, where an INFO line is dropped
        before any handler sees it - including Sentry's log stream. A page the
        user reports by reference has to outlive that threshold.
        """
        rendered(
            code="sso_state_mismatch",
            status=400,
            log_message="OAuth callback rejected: %s",
            log_args=("OAuth state parameter mismatch",),
        )

        assert levels(caplog) == {logging.WARNING}

    def test_a_5xx_logs_at_error(self, rendered, caplog):
        """ERROR is what opens the Sentry issue, so it is reserved for 5xx."""
        rendered(code="sso_unexpected", status=500)

        assert levels(caplog) == {logging.ERROR}

    def test_the_reference_on_the_page_is_the_one_in_the_log(self, rendered, caplog):
        """Support is given the reference, so it has to find the log line."""
        response = rendered(code="sso_state_mismatch", status=400)

        error = json.loads(WINDOW_INIT_ERROR.search(response.get_data(as_text=True)).group(1))
        assert caplog.records[0].context["reference"] == error["reference"]
