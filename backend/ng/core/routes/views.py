"""
All user-accessed URLs use the same view for the frontend application.
"""

from typing import Any
from flask import Blueprint, render_template
from flask import current_app as app
from CTFd.utils import get_app_config

plugin_views = Blueprint("plugin_views", __name__)


@plugin_views.route("/hello", defaults={"subpath": ""}, methods=["GET"], strict_slashes=False)
@plugin_views.route("/hello/<path:subpath>", methods=["GET"])
def view_template(subpath: str) -> Any:
    static_build_path = get_app_config("STATIC_BUILD_PATH")
    return render_template(
        "dev_entrypoint.html" if app.debug else "prod_entrypoint.html",
        static_build_path=static_build_path,
    )
