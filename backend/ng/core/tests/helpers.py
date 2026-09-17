"""
Test helper functions for setting up the plugin's test environment.
"""

from pathlib import Path

import jinja2
from flask import g
from tests.helpers import (
    create_ctfd as create_ctfd_original,
)
from tests.helpers import (
    destroy_ctfd as destroy_ctfd_original,
)
from tests.helpers import (
    setup_ctfd,
)


def plugin_load(app):
    """Load the plugin into the app context."""
    try:
        from ... import load

        load(app)
    except Exception as e:
        print(f"Plugin load failed: {e}")
        import traceback

        traceback.print_exc()
        raise


def register_frontend_templates(app):
    """
    Put the frontend entrypoint templates on the app's template path.

    A deployed image copies `backend/views` into the active theme's template
    directory (see `dockerfiles/ctfd.Dockerfile`), which is how the frontend
    shell resolves at runtime. Tests run against the CTFd source tree, where
    that copy never happened, so point Jinja straight at the directory.
    """
    views = Path(__file__).resolve().parents[3] / "views"

    app.jinja_loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(str(views)),
        app.jinja_loader,
    ])


def create_ctfd():
    """Prepares the Flask app instance for the test session."""

    app = create_ctfd_original(enable_plugins=True, setup=False)

    register_frontend_templates(app)

    # Disable rate limiters for testing
    app.config["RATELIMIT_ENABLED"] = False

    with app.app_context():
        plugin_load(app)

    # the fixtures hold one app context across many requests, so g would otherwise outlive a request
    @app.before_request
    def clear_ng_request_memos():
        g.pop("_ng_current_user", None)
        g.pop("_ng_user_by_ctfd_id", None)

    app = setup_ctfd(
        app,
        ctf_name="CTFd",
        ctf_description="CTF description",
        name="admin",
        email="admin@examplectf.com",
        password="password",
        user_mode="users",
        ctf_theme=None,
    )

    return app


def destroy_ctfd(app):
    """Performs final cleanup after the entire test session is complete."""

    return destroy_ctfd_original(app)


def login_as(client, user):
    """Utility function to log in a specific user into a test client's session."""

    with client.session_transaction() as sess:
        sess["id"] = user.id
        sess["name"] = user.name
        sess["type"] = getattr(user, "type", "user")
        sess["nonce"] = "test-nonce"
