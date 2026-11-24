"""
Tests for post-login redirect target validation
"""

import pytest

from ..utils.redirect import safe_redirect_target


@pytest.fixture
def route_prefix(app, monkeypatch):
    """Run checks in an app context, with the app served under the given route prefix."""
    def serve_under(prefix):
        monkeypatch.setitem(app.config, "ROUTE_PREFIX", prefix)

    with app.app_context():
        yield serve_under


@pytest.mark.parametrize("target", [
    "/ctf",
    "/ctf/",
    "/ctf/events/5/challenge/12",
    "/ctf/support?tab=open#latest",
    "/ctf/events/my%20event",
    "/ctf/search?q=a%2F%2Fb%5Cc",
])
def test_accepts_app_pages(route_prefix, target):
    """
    Test that paths to app pages under the route prefix are accepted unchanged
    """
    route_prefix("/ctf")

    assert safe_redirect_target(target) == target


@pytest.mark.parametrize("target", [
    None,
    "",
    42,
    "ctf/events",
    "https://evil.example.com/ctf/events",
    "//evil.example.com/ctf/events",
    "/\\evil.example.com/ctf/events",
    "/ctf\\..\\events",
    "/\t/evil.example.com",
    "/ctf/events\r\nSet-Cookie: x=1",
    "javascript:alert(1)",
    "/other/events",
    "/ctfevil",
    "/ctf/../other",
    "/ctf/%2e%2e/other",
    "/ctf/ng",
    "/ctf/ng/users/logout",
    "/ctf/%6E%67/users/me",
    "/ctf/%6e%67",
    "/ctf%2Fng/users/me",
    "/%2fevil.example.com",
    "/%2F%2Fevil.example.com",
    "/%5Cevil.example.com",
    "/ctf/%5C..%5Cother",
    "/ctf/%0d%0aSet-Cookie:%20x=1",
    "/ctf//ng/users/me",
    "/ctf///ng/users/me",
    "/ctf/%2Fng/users/me",
    "/ctf/events//5",
])
def test_rejects_unsafe_targets(route_prefix, target):
    """
    Test that targets off-site, outside the route prefix, or at backend
    endpoints are rejected
    """
    route_prefix("/ctf")

    assert safe_redirect_target(target) is None


def test_without_route_prefix(route_prefix):
    """
    Test that every app page is a valid target when the app is served from the
    site root, but backend endpoints still are not
    """
    route_prefix("")

    assert safe_redirect_target("/events/5") == "/events/5"
    assert safe_redirect_target("/ng/users/me") is None
    assert safe_redirect_target("/%6E%67/users/me") is None
    assert safe_redirect_target("/%2Fevil.example.com") is None
