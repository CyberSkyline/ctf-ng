"""
All user-accessed URLs use the same view for the frontend application.
"""

from typing import Any
from flask import Blueprint, render_template
from flask import current_app as app, session, request
from sqlalchemy.exc import IntegrityError
from CTFd.utils import get_app_config
from CTFd.models import Admins, db
from CTFd.utils.security.csrf import generate_nonce

plugin_views = Blueprint("plugin_views", __name__)


@plugin_views.route("/", defaults={"subpath": ""}, methods=["GET"], strict_slashes=False)
@plugin_views.route("/<path:subpath>", methods=["GET"])
def view_template(subpath: str) -> Any:
    static_build_path = get_app_config("STATIC_BUILD_PATH")
    return render_template(
        "dev_entrypoint.html" if app.debug else "prod_entrypoint.html",
        static_build_path=static_build_path,
    )

@plugin_views.route("/setup", methods=["GET", "POST"])
def setup():
    static_build_path = get_app_config("STATIC_BUILD_PATH")
    if not session.get("nonce"):
        session["nonce"] = generate_nonce()
    if request.method == "POST":

        # Administration
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]


        admin = Admins(
            name=name, email=email, password=password, type="admin", hidden=True
        )

        try:
            db.session.add(admin)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    return render_template(
        "dev_entrypoint.html" if app.debug else "prod_entrypoint.html",
        static_build_path=static_build_path,
    )


