"""
Validation for post-login redirect targets, shared by every login flow.
"""

from urllib.parse import unquote, urlsplit

from flask import current_app


def _is_under(path, prefix):
    """Whether the path is `prefix` itself or nested under it. An empty prefix contains every path."""
    return path == prefix or path.startswith(f"{prefix}/")


def safe_redirect_target(target):
    """
    Returns the target if it is a path to a page of the app on this site, otherwise None.

    Guards against open redirects through a crafted `?redirect=` param, and keeps it from pointing at
    backend endpoints rather than app routes.
    """
    if not isinstance(target, str) or not target.startswith("/") or target.startswith(("//", "/\\")):
        return None

    # browsers strip or reinterpret these, which can turn a path into a different host
    if any(c == "\\" or ord(c) < 0x20 or ord(c) == 0x7F for c in target):
        return None

    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return None

    # `..` segments (encoded or not) could climb out of the route prefix
    if any(segment in (".", "..") for segment in unquote(parts.path).split("/")):
        return None

    prefix = current_app.config.get("ROUTE_PREFIX") or ""
    if not _is_under(parts.path, prefix) or _is_under(parts.path, f"{prefix}/ng"):
        return None

    return target
