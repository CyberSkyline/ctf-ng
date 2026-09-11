# backend/ng/user/controllers/authenticate.py
import os

from CTFd.cache import clear_user_session
from CTFd.models import Users as User
from CTFd.models import db
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import hmac
from flask import redirect, request, session
from requests_oauthlib import OAuth2Session

from ...core.exceptions import AuthenticationError
from ...core.utils.error_page import render_error_page
from ..models.User import User as NG_User

OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
OKTA_CLIENT_SECRET = os.getenv("OKTA_CLIENT_SECRET")
OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")
# External URL where users can register an SSO account.
SSO_REGISTRATION_URL = os.getenv("SSO_REGISTRATION_URL")
ROUTE_PREFIX = os.getenv("ROUTE_PREFIX")
AUTHORIZATION_BASE_URL = f"{OKTA_DOMAIN}/oauth2/v1/authorize"
TOKEN_URL = f"{OKTA_DOMAIN}/oauth2/v1/token"
USER_API_URL = f"{OKTA_DOMAIN}/oauth2/v1/userinfo"
REDIRECT_URI = f"{SERVER_DOMAIN}{ROUTE_PREFIX}/ng/authenticate/okta/callback"
SCOPE = ["openid", "profile", "email"]

# bcrypt-like placeholder hash
OAUTH_PLACEHOLDER_HASH = "$2b$12$OAuthPlaceholderHashForCTFd0000"


def okta_login():
    okta = OAuth2Session(
        OKTA_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )
    authorization_url, state = okta.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type="offline",
        prompt="login consent"
    )
    session["oauth_state"] = state

    return redirect(authorization_url)

def okta_register():
    if not SSO_REGISTRATION_URL:
        return render_error_page(
            "sso_registration_unavailable",
            status=503,
            log_message="SSO registration requested but SSO_REGISTRATION_URL is not set",
        )

    return redirect(SSO_REGISTRATION_URL)

def okta_register_card():
    if not SSO_REGISTRATION_URL:
        return render_error_page(
            "sso_registration_unavailable",
            status=503,
            log_message="SSO registration requested but SSO_REGISTRATION_URL is not set",
        )

    return redirect(f"{SSO_REGISTRATION_URL.rstrip('/')}/piv")

def okta_callback():
    email = None
    oauth_id = None
    user_data = None
    name = None
    ng_user = None
    ctfd_user = None

    okta_code = request.args.get("code")
    okta_state_param = request.args.get("state")
    okta_error = request.args.get("error")
    okta_error_description = request.args.get("error_description")
    okta_session_state = session.get("oauth_state")

    error_msg = ""
    error_code = ""

    if okta_error:
        # Generic Okta error
        error_msg = f"Okta returned error: {okta_error}"
        if okta_error_description:
            error_msg += f" - {okta_error_description}"
        error_code = "sso_generic_error"

        # More specialized okta error messages
        if okta_error == "access_denied" and okta_error_description == "The resource owner or authorization server denied the request":
            error_msg = "PIV/CAC card verification required"
            error_code = "sso_card_error"
    elif not okta_session_state:
        error_msg = "No OAuth state found in session"
        error_code = "sso_state_missing"
    elif okta_state_param != okta_session_state:
        error_msg = "OAuth state parameter mismatch"
        error_code = "sso_state_mismatch"
    elif not okta_code:
        error_msg = "No authorization code found in callback URL"
        error_code = "sso_no_code"

    if (error_msg):
        return render_error_page(
            error_code,
            status=400,
            log_message=f"OAuth callback rejected: {error_msg}",
            context={
                "has_oauth_state": 'oauth_state' in session,
                # The authorization code is a credential, so it is left out.
                "request_args": {k: v for k, v in request.args.items() if k != "code"},
            },
            detail=error_msg,
        )

    try:
        # Parse Okta data
        okta = OAuth2Session(
            OKTA_CLIENT_ID,
            state=session['oauth_state'],
            redirect_uri=REDIRECT_URI
        )

        okta.fetch_token(
            TOKEN_URL,
            code=okta_code,
            client_secret=OKTA_CLIENT_SECRET,
            authorization_response=request.url,
            include_client_id=True
        )
        user_data = okta.get(USER_API_URL).json()

        email = user_data.get("email")
        name = user_data.get("name", "N/A")
        oauth_id = user_data.get("sub")
        if not email:
            raise AuthenticationError(f"No email found in user info response. OAuth ID: {oauth_id}")

        if not oauth_id:
            raise AuthenticationError(f"No oauth id in user info response. Email: {email}")

        # Check for existing user
        ng_user = NG_User.query.filter_by(oauth_id=oauth_id).first()

        if not ng_user:
            ctfd_user = User(
                name=name,
                email=email,
                password=OAUTH_PLACEHOLDER_HASH,
                verified=True
            )
            db.session.add(ctfd_user)
            db.session.flush()

            ng_user = NG_User.find_or_create_by_ctfd_id(ctfd_user.id)
            ng_user.oauth_id = oauth_id
        else:
            ctfd_user = User.query.filter_by(id=ng_user.id).first()

        # ctfd_user.last_login = datetime.datetime.now(datetime.UTC)
        # ctfd_user.email = email

        # Clear session and set up new authenticated session
        session.clear()
        session['id'] = ctfd_user.id
        session['nonce'] = generate_nonce()
        session['hash'] = hmac(ctfd_user.password)
        session.permanent = True

        clear_user_session(user_id=ctfd_user.id)

        db.session.commit()

        return redirect(f"{SERVER_DOMAIN}{ROUTE_PREFIX}")
    except AuthenticationError as e:
        db.session.rollback()

        return render_error_page(
            "sso_auth_failed",
            status=e.status_code,
            log_message=f"AuthenticationError during OAuth: {str(e)}",
            detail=str(e),
            exc_info=True,
        )
    except Exception as e:
        db.session.rollback()

        failure_stage = "unknown"
        if user_data is None:
            failure_stage = "okta_user_data_fetch"
        elif not email or not oauth_id:
            failure_stage = "user_data_validation"
        elif ng_user is None:
            failure_stage = "user_lookup"
        elif ctfd_user is None:
            failure_stage = "ctfd_user_creation"
        else:
            failure_stage = "session_setup_or_commit"

        return render_error_page(
            "sso_unexpected",
            status=500,
            log_message=f"Unexpected error during OAuth at stage '{failure_stage}': {str(e)}",
            context={
                "failure_stage": failure_stage,
                "email": email,
                "oauth_id": oauth_id,
            },
            detail=f"{type(e).__name__} at stage '{failure_stage}': {str(e)}",
            exc_info=True,
        )
    finally:
        db.session.close()