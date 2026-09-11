"""
Tests for the frontend entrypoint templates.
"""

import json
import re

import pytest
from flask import render_template

WINDOW_INIT_ERROR = re.compile(r"error:\s*(\{.*?\}|null)\s*\n", re.DOTALL)


@pytest.mark.parametrize("template", ["dev_entrypoint.html", "prod_entrypoint.html"])
def test_entrypoint_renders_without_an_error_argument(app, template):
    """
    Test that the entrypoint templates tolerate being rendered without `error`.

    `tojson` raises on an undefined value, so a caller that does not know about
    the argument would otherwise get a 500 instead of the app.
    """
    with app.test_request_context():
        body = render_template(template)

    assert json.loads(WINDOW_INIT_ERROR.search(body).group(1)) is None
