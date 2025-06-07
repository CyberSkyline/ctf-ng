# /plugin/routes/__init__.py

from flask import Blueprint
from flask_restx import Api
from typing import Any

from .api.teams import teams_namespace
from .api.worlds import worlds_namespace
from .api.users import users_namespace
from .api.admin import admin_namespace

api_blueprint = Blueprint("plugin_api", __name__)

# docs
api_v1 = Api(
    api_blueprint,
    version="1.0",
    title="CTFd Plugin API",
    description="The API for CTF-NG. Used to manage worlds, teams, scoring, and other features for our custom plugin.",
    doc="/docs",
    authorizations={"sessionAuth": {"type": "apiKey", "in": "cookie", "name": "session"}},
    security=["sessionAuth"],
)


api_v1.add_namespace(teams_namespace, path="/teams")
api_v1.add_namespace(worlds_namespace, path="/worlds")
api_v1.add_namespace(users_namespace, path="/users")
api_v1.add_namespace(admin_namespace, path="/admin")


def delete_unwanted_ctfd_routes(app: Any) -> None:
    pass
