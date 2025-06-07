# /plugin/tests/helpers.py

from plugin import load as plugin_load

from tests.helpers import (
    create_ctfd as create_ctfd_original,
    destroy_ctfd as destroy_ctfd_original,
    setup_ctfd,
)


def create_ctfd():
    """Prepares the Flask app instance for the test session."""

    app = create_ctfd_original(enable_plugins=True, setup=False)

    with app.app_context():
        plugin_load(app)

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
