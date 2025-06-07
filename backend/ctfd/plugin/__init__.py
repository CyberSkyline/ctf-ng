#!/usr/bin/env python3

from .routes import delete_unwanted_ctfd_routes, api_blueprint
from .routes.views import plugin_views
from CTFd.models import db
from typing import Tuple, Any


def _create_tables() -> Tuple[Any, Any, Any, Any]:
    from .models.World import World
    from .models.Team import Team
    from .models.User import User
    from .models.TeamMember import TeamMember

    return (
        World,
        Team,
        User,
        TeamMember,
    )


def load(app: Any) -> None:
    try:
        delete_unwanted_ctfd_routes(app)

        print("Loading plugin...", flush=True)

        _create_tables()
        db.create_all()

        app.register_blueprint(plugin_views)
        app.register_blueprint(api_blueprint, url_prefix="/plugin/api")
        print("Plugin loaded successfully", flush=True)
    except Exception as e:
        print("Error loading plugin:", e, flush=True)
