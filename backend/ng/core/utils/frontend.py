"""
Renders the frontend single-page application shell.

Routes that a browser navigates to directly return this rather than JSON, so
the user gets the app instead of a raw response body.
"""

from CTFd.utils import get_app_config
from flask import current_app as app
from flask import render_template

from .current_user import get_current_user


def render_frontend(*, error: dict | None = None) -> str:
    """
    Render the SPA entrypoint template.

    Args:
        error: A failure for the app to display instead of the routed page.
            Serialized into `window.init.error`, where the frontend picks it up.
            Passing it through the document rather than the query string keeps
            it off the URL, where a visitor could edit it.

    Returns:
        The rendered HTML document.
    """
    user = get_current_user()

    return render_template(
        "dev_entrypoint.html" if app.debug else "prod_entrypoint.html",
        static_build_path=get_app_config("STATIC_BUILD_PATH"),
        user_id=user.id if user else None,
        error=error,
    )
