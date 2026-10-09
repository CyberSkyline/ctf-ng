from flask import g, has_request_context, session
from werkzeug.routing import BuildError

from CTFd.utils.user import get_current_user as _ctfd_get_current_user

from ..exceptions import AuthenticationError


def _get_session_user():
    try:
        return _ctfd_get_current_user()
    except BuildError:
        # CTFd ends a session whose password has changed by redirecting non-JSON requests to its
        # login page, but the plugin removes that blueprint. Answer with a 401 as it does for JSON.
        if "id" in session:
            raise
        raise AuthenticationError("Your session has expired. Please log in again.") from None


def get_current_user():
    """Per-request memo over CTFd's get_current_user, which requeries on every call."""
    if not has_request_context():
        return _ctfd_get_current_user()

    if "_ng_current_user" not in g:
        g._ng_current_user = _get_session_user()
    return g._ng_current_user
