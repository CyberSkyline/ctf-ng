from flask import g, has_request_context

from CTFd.utils.user import get_current_user as _ctfd_get_current_user


def get_current_user():
    """Per-request memo over CTFd's get_current_user, which requeries on every call."""
    if not has_request_context():
        return _ctfd_get_current_user()

    if "_ng_current_user" not in g:
        g._ng_current_user = _ctfd_get_current_user()
    return g._ng_current_user
