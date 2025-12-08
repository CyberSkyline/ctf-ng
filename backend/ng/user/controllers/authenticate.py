# backend/ng/user/controllers/authenticate.py
import datetime
import os

from CTFd.cache import clear_user_session
from CTFd.models import Users as User
from CTFd.models import db
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import hmac
from flask import redirect, request, session
from requests_oauthlib import OAuth2Session

from ..models.User import User as NG_User

OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
OKTA_CLIENT_SECRET = os.getenv("OKTA_CLIENT_SECRET")
OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")
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

def okta_callback():
    error_msg = None
    if 'oauth_state' not in session:
        error_msg = "No OAuth state found in session - possible session timeout"

    if 'error' in request.args:
        error_msg = f"Okta returned error: {request.args.get('error')}"
        if 'error_description' in request.args:
            error_msg += f" - {request.args.get('error_description')}"

    code = request.args.get('code')
    if not code:
        error_msg = "No authorization code found in callback URL"

    if (error_msg):
        print(error_msg)
        return {"error": error_msg}, 400

    try:
        # Parse Okta data
        okta = OAuth2Session(
            OKTA_CLIENT_ID,
            state=session['oauth_state'],
            redirect_uri=REDIRECT_URI
        )

        okta.fetch_token(
            TOKEN_URL,
            code=code,
            client_secret=OKTA_CLIENT_SECRET,
            authorization_response=request.url,
            include_client_id=True
        )
        user_data = okta.get(USER_API_URL).json()

        email = user_data.get("email")
        name = user_data.get("name", "N/A")
        oauth_id = user_data.get("sub")
        if not email:
            error_msg = "No email found in user info response"
            print(error_msg)
            return {"error": error_msg}, 400

        if not oauth_id:
            error_msg = "No oauth id in user info response"
            print(error_msg)
            return {"error": error_msg}, 400

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

        ctfd_user.last_login = datetime.datetime.now(datetime.UTC)
        ctfd_user.email = email
        session.clear()

        session['id'] = ctfd_user.id
        session['nonce'] = generate_nonce()
        session['hash'] = hmac(ctfd_user.password)
        session.permanent = True
        clear_user_session(user_id=ctfd_user.id)

        db.session.commit()

        return redirect(f"{SERVER_DOMAIN}{ROUTE_PREFIX}")
    except Exception as e:
        db.session.rollback()
        error_msg = f"Authentication failed: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return {"error": "Authentication failed", "details": str(e)}, 400
    finally:
        db.session.close()