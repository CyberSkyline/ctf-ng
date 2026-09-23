"""
Tests for the Okta authentication routes
"""

import json
import re

from CTFd.models import Users

from ..controllers import authenticate
from ..models.User import User as NgUser

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


class FakeOktaSession:
    """A stand-in for OAuth2Session that skips the real token exchange and
    returns canned userinfo. Doubles as its own response object, since
    `.get(...)` only ever needs to yield something with `.json()`."""

    def __init__(self, user_data):
        self.user_data = user_data

    def fetch_token(self, *_args, **_kwargs):
        return {"access_token": "fake-token"}

    def get(self, *_args, **_kwargs):
        return self

    def json(self):
        return self.user_data


def do_okta_callback(client, monkeypatch, *, email, oauth_id, name="N/A"):
    """
    Drive a successful Okta callback (valid state, valid code) with the given
    userinfo response, and return the resulting response.
    """
    monkeypatch.setattr(
        authenticate,
        "OAuth2Session",
        lambda *_args, **_kwargs: FakeOktaSession({"email": email, "sub": oauth_id, "name": name}),
    )

    with client.session_transaction() as sess:
        sess["oauth_state"] = "expected-state"

    return client.get("/ng/authenticate/okta/callback?code=abc&state=expected-state")


def make_sso_user(user_factory, db_session, *, name, email, oauth_id=None):
    """Create a user with the given oauth id (or none, for a plain local
    account) and return their id."""
    ng_user = user_factory(name=name, email=email)
    ng_user.oauth_id = oauth_id
    db_session.commit()
    return ng_user.id


def assert_logged_in_as(client, user_id):
    with client.session_transaction() as sess:
        assert sess["id"] == user_id


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


def test_callback_creates_new_user_when_no_oauth_id_or_email_match(public_client, monkeypatch, db_session):
    """
    Test that a brand new Okta identity with no matching oauth id or email
    creates a new local account and logs in as it.
    """
    response = do_okta_callback(
        public_client, monkeypatch, email="new.user@example.com", oauth_id="okta|new-user", name="New User"
    )

    assert response.status_code == 302

    ctfd_user = Users.query.filter_by(email="new.user@example.com").first()
    assert ctfd_user is not None
    assert ctfd_user.name == "New User"
    assert ctfd_user.ng_users.oauth_id == "okta|new-user"

    assert_logged_in_as(public_client, ctfd_user.id)


def test_callback_logs_in_existing_oauth_user_unchanged(public_client, monkeypatch, db_session, user_factory):
    """
    Test that a returning SSO user with an unchanged email just logs in, with
    no changes made to their record.
    """
    user_id = make_sso_user(user_factory, db_session, name="Returning User", email="returning@example.com", oauth_id="okta|returning")

    response = do_okta_callback(public_client, monkeypatch, email="returning@example.com", oauth_id="okta|returning")

    assert response.status_code == 302
    assert_logged_in_as(public_client, user_id)

    assert Users.query.filter_by(email="returning@example.com").count() == 1
    assert NgUser.query.get(user_id).oauth_id == "okta|returning"


def test_callback_syncs_email_when_oauth_id_matches(public_client, monkeypatch, db_session, user_factory):
    """
    Test that when the oauth id matches but Okta reports a new email (and
    nobody else owns it), the local account's email is updated to match.
    """
    user_id = make_sso_user(user_factory, db_session, name="Changed Email User", email="old@example.com", oauth_id="okta|changed-email")

    response = do_okta_callback(public_client, monkeypatch, email="new@example.com", oauth_id="okta|changed-email")

    assert response.status_code == 302
    assert_logged_in_as(public_client, user_id)

    refreshed = NgUser.query.get(user_id)
    assert refreshed.ctfd_user.email == "new@example.com"
    assert refreshed.oauth_id == "okta|changed-email"


def test_callback_reassigns_oauth_id_when_new_email_collides(public_client, monkeypatch, db_session, user_factory):
    """
    Test that when the oauth id matches but Okta's email now belongs to a
    different existing account, that other account takes over the oauth id
    and the originally-matched account reverts to a plain local account.
    """
    stale_id = make_sso_user(user_factory, db_session, name="Stale Identity", email="stale@example.com", oauth_id="okta|shared")
    owner_id = make_sso_user(user_factory, db_session, name="Email Owner", email="owner@example.com")

    response = do_okta_callback(public_client, monkeypatch, email="owner@example.com", oauth_id="okta|shared")

    assert response.status_code == 302
    assert_logged_in_as(public_client, owner_id)

    refreshed_stale = NgUser.query.get(stale_id)
    assert refreshed_stale.oauth_id is None
    assert refreshed_stale.ctfd_user.email == "stale@example.com"

    refreshed_owner = NgUser.query.get(owner_id)
    assert refreshed_owner.oauth_id == "okta|shared"
    assert refreshed_owner.ctfd_user.email == "owner@example.com"


def test_callback_takes_over_local_account_by_email_fallback(public_client, monkeypatch, db_session, user_factory):
    """
    Test that when no oauth id matches (e.g. Okta issued a new one), a local
    account found by email is taken over rather than a duplicate being
    created - this is the case Okta's breakage actually hit.
    """
    user_id = make_sso_user(user_factory, db_session, name="Local User", email="local@example.com")
    assert NgUser.query.get(user_id).oauth_id is None

    response = do_okta_callback(public_client, monkeypatch, email="local@example.com", oauth_id="okta|reissued")

    assert response.status_code == 302
    assert_logged_in_as(public_client, user_id)

    assert Users.query.filter_by(email="local@example.com").count() == 1
    assert NgUser.query.get(user_id).oauth_id == "okta|reissued"


def test_callback_overwrites_stale_oauth_id_on_email_fallback(public_client, monkeypatch, db_session, user_factory):
    """
    Test that the email fallback takeover overwrites an existing (stale)
    oauth id on the matched account, not just a null one.
    """
    user_id = make_sso_user(user_factory, db_session, name="Existing SSO User", email="existing@example.com", oauth_id="okta|old-id")

    response = do_okta_callback(public_client, monkeypatch, email="existing@example.com", oauth_id="okta|new-id")

    assert response.status_code == 302
    assert_logged_in_as(public_client, user_id)
    assert NgUser.query.get(user_id).oauth_id == "okta|new-id"
