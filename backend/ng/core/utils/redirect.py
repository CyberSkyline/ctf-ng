"""
Validation for post-login redirect targets, shared by every login flow.
"""

from urllib.parse import unquote, urlsplit

from flask import current_app


def _is_under(path, prefix):
    """Whether the path is `prefix` itself or nested under it. An empty prefix contains every path."""
    return path == prefix or path.startswith(f"{prefix}/")


def _has_unsafe_chars(value):
    """Whether the value has backslashes or control characters, which browsers strip or reinterpret in ways that can
    turn a path into a different host."""
    return any(c == "\\" or ord(c) < 0x20 or ord(c) == 0x7F for c in value)


def _is_app_path(path, prefix):
    """
    Whether the path is a plain same-site path to an app page under the prefix, rather than one a browser could read
    as another host, one that climbs out of the prefix, or one at a backend endpoint.
    """
    # a leading `//` is read as another host, and nginx and Werkzeug both merge a `//` anywhere else, so
    # `/ctf//ng` would reach `/ng` while slipping past the prefix checks below
    if not path.startswith("/") or "//" in path:
        return False

    if _has_unsafe_chars(path):
        return False

    # `..` segments could climb out of the route prefix
    if any(segment in (".", "..") for segment in path.split("/")):
        return False

    return _is_under(path, prefix) and not _is_under(path, f"{prefix}/ng")


def safe_redirect_target(target):
    """
    Returns the target if it is a path to a page of the app on this site, otherwise None.

    Guards against open redirects through a crafted `?redirect=` param, and keeps it from pointing at
    backend endpoints rather than app routes.
    """
    if not isinstance(target, str):
        return None

    # the raw target must be plain before it is split, so nothing ahead of the path can be read as a host
    if _has_unsafe_chars(target):
        return None

    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return None

    # Browsers may decode the path before following it (`/ctf/%6E%67` becomes `/ctf/ng`, `/%2Fevil.com` could become
    # `//evil.com`), so it must pass as written and decoded. The target is still returned as written.
    prefix = current_app.config.get("ROUTE_PREFIX") or ""
    if not (_is_app_path(parts.path, prefix) and _is_app_path(unquote(parts.path), prefix)):
        return None

    return target
