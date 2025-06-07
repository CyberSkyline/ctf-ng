"""
All user-accessed URLs use the same view
"""

from flask import Blueprint, render_template
from typing import Any

plugin_views = Blueprint("plugin_views", __name__)


@plugin_views.route("/hello", defaults={"subpath": ""}, methods=["GET"], strict_slashes=False)
@plugin_views.route("/hello/<path:subpath>", methods=["GET"])
def view_template(subpath: str) -> Any:
    return render_template("entrypoint.html")
