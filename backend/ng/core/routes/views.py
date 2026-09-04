"""
All user-accessed URLs use the same view for the frontend application.
"""

from typing import Any

from flask import Blueprint

from ..utils.frontend import render_frontend

plugin_views = Blueprint("plugin_views", __name__)


@plugin_views.route("/", defaults={"subpath": ""}, methods=["GET"], strict_slashes=False)
@plugin_views.route("/<path:subpath>", methods=["GET"])
def view_template(subpath: str) -> Any:
    return render_frontend()
