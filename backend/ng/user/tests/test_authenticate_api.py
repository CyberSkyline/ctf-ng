"""
Tests for the Okta authentication routes
"""

from ..controllers import authenticate


def test_sso_register_redirects_to_configured_url(public_client, monkeypatch):
    """
    Test that the register endpoint redirects to the configured registration URL
    """
    monkeypatch.setattr(authenticate, "SSO_REGISTRATION_URL", "https://sso.example.com/register")

    response = public_client.get("/ng/authenticate/okta/register")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://sso.example.com/register"


def test_sso_register_without_configured_url(public_client, monkeypatch):
    """
    Test that the register endpoint reports a 404 when no registration URL is configured
    """
    monkeypatch.setattr(authenticate, "SSO_REGISTRATION_URL", None)

    response = public_client.get("/ng/authenticate/okta/register")

    assert response.status_code == 404
