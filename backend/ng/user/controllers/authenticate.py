# backend/ng/user/controllers/authenticate.py
from flask import redirect, request, session
from requests_oauthlib import OAuth2Session
import os
import datetime
from CTFd.cache import clear_user_session
from CTFd.utils.security.signing import hmac
from CTFd.utils.security.csrf import generate_nonce
from CTFd.models import db
from CTFd.models import Users as User
from ..models.User import User as NG_User

OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
OKTA_CLIENT_SECRET = os.getenv("OKTA_CLIENT_SECRET")
OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")
AUTHORIZATION_BASE_URL = f"{OKTA_DOMAIN}/oauth2/v1/authorize"
TOKEN_URL = f"{OKTA_DOMAIN}/oauth2/v1/token"
USER_API_URL = f"{OKTA_DOMAIN}/oauth2/v1/userinfo"
REDIRECT_URI = f"{SERVER_DOMAIN}/ng/authenticate/okta/callback"
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
        if not email:
            error_msg = "No email found in user info response"
            print(error_msg)
            return {"error": error_msg}, 400

        name = user_data.get("name", "N/A")
        oauth_id = user_data.get("sub")

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name=name,
                email=email,
                password=OAUTH_PLACEHOLDER_HASH,
                verified=True
            )
            db.session.add(user)
            db.session.flush()

        NG_User_obj = NG_User.find_or_create_by_ctfd_id(user.id)
        user_data = okta.get(USER_API_URL).json()

        email = user_data.get("email")
        if not email:
            error_msg = "No email found in user info response"
            print(error_msg)
            return {"error": error_msg}, 400

        name = user_data.get("name", "N/A")
        oauth_id = user_data.get("sub")

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name=name,
                email=email,
                password=OAUTH_PLACEHOLDER_HASH,
                verified=True
            )
            db.session.add(user)
            db.session.flush()
        else:
            if user.name != name:
                user.name = name

        NG_User_obj = NG_User.find_or_create_by_ctfd_id(user.id)
        NG_User_obj.name = name
        NG_User_obj.email = email
        NG_User_obj.oauth_id = oauth_id

        user.last_login = datetime.datetime.now(datetime.UTC)
        session.clear()

        session['id'] = user.id
        session['nonce'] = generate_nonce()
        session['hash'] = hmac(user.password)
        session.permanent = True
        clear_user_session(user_id=user.id)

        db.session.commit()

        return redirect("/hello") # TODO: update this when the vite entrypoint is updated


    except Exception as e:
        db.session.rollback()
        error_msg = f"Authentication failed: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return {"error": "Authentication failed", "details": str(e)}, 400
    finally:
        db.session.close()