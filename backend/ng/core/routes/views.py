"""
All user-accessed URLs use the same view for the frontend application.
"""

from typing import Any

from CTFd.utils import get_app_config
from ..utils.current_user import get_current_user
from flask import Blueprint, render_template
from flask import current_app as app

plugin_views = Blueprint("plugin_views", __name__)


@plugin_views.route("/", defaults={"subpath": ""}, methods=["GET"], strict_slashes=False)
@plugin_views.route("/<path:subpath>", methods=["GET"])
def view_template(subpath: str) -> Any:
    static_build_path = get_app_config("STATIC_BUILD_PATH")
    user = get_current_user()
    return render_template(
        "dev_entrypoint.html" if app.debug else "prod_entrypoint.html",
        static_build_path=static_build_path,
        user_id=user.id if user else None,
    )


