# /plugin/tests/helpers.py
from .. import load as plugin_load
from sqlalchemy.schema import CreateTable
from CTFd.models import db

from tests.helpers import (
    create_ctfd as create_ctfd_original,
    destroy_ctfd as destroy_ctfd_original,
    setup_ctfd,
)


def create_ctfd():
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
    for table in db.metadata.sorted_tables:
        print(CreateTable(table).compile(compile_kwargs={"literal_binds": True}))
    return destroy_ctfd_original(app)


def get_models():
    """model classes from the database registry"""
    models = {}

    for mapper in db.Model.registry.mappers:
        model_class = mapper.class_
        if hasattr(model_class, "__tablename__"):
            if model_class.__tablename__ == "ng_worlds":
                models["World"] = model_class
            elif model_class.__tablename__ == "ng_teams":
                models["Team"] = model_class
            elif model_class.__tablename__ == "ng_users":
                models["User"] = model_class
            elif model_class.__tablename__ == "ng_team_members":
                models["TeamMember"] = model_class

    return models
