# /plugin/routes/api/__init__.py

from .teams import teams_namespace
from .worlds import worlds_namespace
from .users import users_namespace
from .admin import admin_namespace

__all__ = ["teams_namespace", "worlds_namespace", "users_namespace", "admin_namespace"]
