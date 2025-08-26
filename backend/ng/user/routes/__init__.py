from .admin_routes import users_admin_namespace
from .user_routes import users_user_namespace
from .authenticate import oauth_namespace

__all__ = [
    "users_admin_namespace",
    "users_user_namespace",
    "oauth_namespace",
]