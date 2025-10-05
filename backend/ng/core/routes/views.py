"""
All user-accessed URLs use the same view for the frontend application.
"""

from typing import Any
from flask import Blueprint, render_template
from flask import current_app as app, session, request
from sqlalchemy.exc import IntegrityError
from CTFd.utils import get_app_config
from CTFd.models import Users, Admins, db
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils import validators

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

        name_len = len(name) == 0
        names = (
            Users.query.add_columns(Users.name, Users.id)
            .filter_by(name=name)
            .first()
        )
        emails = (
            Users.query.add_columns(Users.email, Users.id)
            .filter_by(email=email)
            .first()
        )
        pass_short = len(password) == 0
        pass_long = len(password) > 128
        valid_email = validators.validate_email(request.form["email"])
        team_name_email_check = validators.validate_email(name)

        if not valid_email:
            errors.append("Please enter a valid email address")
        if names:
            errors.append("That user name is already taken")
        if team_name_email_check is True:
            errors.append("Your user name cannot be an email address")
        if emails:
            errors.append("That email has already been used")
        if pass_short:
            errors.append("Pick a longer password")
        if pass_long:
            errors.append("Pick a shorter password")
        if name_len:
            errors.append("Pick a longer user name")


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


