"""
Tests for the Okta authentication routes
"""

import json
import re

from ..controllers import authenticate

WINDOW_INIT_ERROR = re.compile(r"error:\s*(\{.*?\}|null)\s*\n", re.DOTALL)


def rendered_error(response) -> dict | None:
    """
    Assert a response is the frontend error page and return the failure it
    carries in `window.init.error`.
    """
    assert response.mimetype == "text/html"

    body = response.get_data(as_text=True)
    match = WINDOW_INIT_ERROR.search(body)
    assert match, f"no window.init.error in response body: {body[:500]}"

    return json.loads(match.group(1))


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
    Test that the register endpoint renders the error page when no registration
    URL is configured
    """
    monkeypatch.setattr(authenticate, "SSO_REGISTRATION_URL", None)

    response = public_client.get("/ng/authenticate/okta/register")

    assert response.status_code == 503
    assert rendered_error(response)["code"] == "sso_registration_unavailable"


def test_sso_register_card_redirects_to_piv_path(public_client, monkeypatch):
    """
    Test that the card registration endpoint redirects to the PIV/CAC path of
    the configured registration URL
    """
    monkeypatch.setattr(authenticate, "SSO_REGISTRATION_URL", "https://sso.example.com/register")

    response = public_client.get("/ng/authenticate/okta/register/card")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://sso.example.com/register/piv"


def test_sso_register_card_ignores_a_trailing_slash(public_client, monkeypatch):
    """
    Test that a registration URL configured with a trailing slash does not
    produce a doubled separator
    """
    monkeypatch.setattr(authenticate, "SSO_REGISTRATION_URL", "https://sso.example.com/register/")

    response = public_client.get("/ng/authenticate/okta/register/card")

    assert response.headers["Location"] == "https://sso.example.com/register/piv"


def test_sso_register_card_without_configured_url(public_client, monkeypatch):
    """
    Test that the card registration endpoint renders the error page when no
    registration URL is configured
    """
    monkeypatch.setattr(authenticate, "SSO_REGISTRATION_URL", None)

    response = public_client.get("/ng/authenticate/okta/register/card")

    assert response.status_code == 503
    assert rendered_error(response)["code"] == "sso_registration_unavailable"


def test_callback_without_session_state(public_client):
    """
    Test that a callback with no OAuth state in the session renders the error page
    """
    response = public_client.get("/ng/authenticate/okta/callback?code=abc&state=xyz")

    assert response.status_code == 400

    error = rendered_error(response)
    assert error["code"] == "sso_state_missing"
    assert error["status"] == 400
    assert error["reference"]


def test_callback_with_generic_error(public_client):
    """
    Test that an error returned by Okta is reported instead of the missing
    authorization code it also causes
    """
    with public_client.session_transaction() as sess:
        sess["oauth_state"] = "expected-state"

    response = public_client.get(
        "/ng/authenticate/okta/callback"
        "?error=access_denied&error_description=User+denied+access&state=expected-state"
    )

    assert rendered_error(response)["code"] == "sso_generic_error"


def test_callback_with_card_error(public_client):
    """
    Test that the access_denied error Okta returns for a missing PIV/CAC
    enrollment is reported as the card error rather than the generic one.

    The description is matched exactly, so this pins the string Okta sends.
    """
    with public_client.session_transaction() as sess:
        sess["oauth_state"] = "expected-state"

    response = public_client.get(
        "/ng/authenticate/okta/callback"
        "?error=access_denied"
        "&error_description=The+resource+owner+or+authorization+server+denied+the+request"
        "&state=expected-state"
    )

    assert rendered_error(response)["code"] == "sso_card_error"


def test_callback_without_authorization_code(public_client):
    """
    Test that a callback missing the authorization code renders the error page
    """
    with public_client.session_transaction() as sess:
        sess["oauth_state"] = "expected-state"

    response = public_client.get("/ng/authenticate/okta/callback?state=expected-state")

    assert rendered_error(response)["code"] == "sso_no_code"


def test_callback_with_mismatched_state(public_client):
    """
    Test that a state parameter that does not match the session renders the error page
    """
    with public_client.session_transaction() as sess:
        sess["oauth_state"] = "expected-state"

    response = public_client.get("/ng/authenticate/okta/callback?code=abc&state=other-state")

    assert rendered_error(response)["code"] == "sso_state_mismatch"


def test_callback_without_a_state_parameter(public_client):
    """
    Test that a callback carrying no state parameter at all is treated as a
    mismatch, rather than skipping the check and failing later in fetch_token
    """
    with public_client.session_transaction() as sess:
        sess["oauth_state"] = "expected-state"

    response = public_client.get("/ng/authenticate/okta/callback?code=abc")

    assert response.status_code == 400
    assert rendered_error(response)["code"] == "sso_state_mismatch"


def test_callback_error_stays_out_of_the_url(public_client):
    """
    Test that the failure is delivered in the document rather than by redirecting
    with it in the query string, so it cannot be read or edited in the URL bar
    """
    response = public_client.get("/ng/authenticate/okta/callback?code=abc&state=xyz")

    assert response.status_code == 400
    assert "Location" not in response.headers


def test_callback_error_omits_internals(app, public_client, monkeypatch):
    """
    Test that outside of debug mode the page carries only the code, status and
    reference - no internal detail, and no authorization code anywhere in it
    """
    monkeypatch.setattr(app, "debug", False)

    response = public_client.get("/ng/authenticate/okta/callback?code=secret-auth-code&state=xyz")

    assert set(rendered_error(response)) == {"code", "status", "reference"}
    assert "secret-auth-code" not in response.get_data(as_text=True)


def test_callback_error_includes_detail_in_debug(app, public_client, monkeypatch):
    """
    Test that debug mode surfaces the internal detail on the page, so developers
    see the specific failure without digging through logs
    """
    monkeypatch.setattr(app, "debug", True)

    response = public_client.get("/ng/authenticate/okta/callback?code=abc&state=xyz")

    assert rendered_error(response)["detail"] == "No OAuth state found in session"


def test_frontend_error_is_absent_on_normal_pages(public_client):
    """
    Test that an ordinary page load leaves window.init.error null, so the app
    routes normally
    """
    response = public_client.get("/")

    assert response.status_code == 200
    assert rendered_error(response) is None


def test_callback_error_detail_cannot_break_out_of_the_script_tag(app, public_client, monkeypatch):
    """
    Test that a failure detail carrying markup is escaped when serialized into
    the document, so provider-supplied text cannot inject script
    """
    monkeypatch.setattr(app, "debug", True)

    with public_client.session_transaction() as sess:
        sess["oauth_state"] = "expected-state"

    response = public_client.get(
        "/ng/authenticate/okta/callback"
        "?error=%3C/script%3E%3Cscript%3Ealert(1)%3C/script%3E&state=expected-state"
    )
    body = response.get_data(as_text=True)

    assert "</script><script>alert(1)</script>" not in body
    # The text still survives intact once the browser parses the JSON string.
    assert "</script><script>alert(1)</script>" in rendered_error(response)["detail"]
