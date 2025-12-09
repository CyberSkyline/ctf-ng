# backend/ng/user/controllers/authenticate.py
import os

from CTFd.cache import clear_user_session
from CTFd.models import Users as User
from CTFd.models import db
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import hmac
from flask import redirect, request, session
from requests_oauthlib import OAuth2Session

from ..models.User import User as NG_User
from ...core.exceptions import AuthenticationError

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
    email = None
    oauth_id = None
    user_data = None
    name = None
    ng_user = None
    ctfd_user = None
    code = None

    error_msg = None
    
    if 'oauth_state' not in session:
        error_msg = "No OAuth state found in session"

    if 'error' in request.args:
        error_msg = f"Okta returned error: {request.args.get('error')}"
        if 'error_description' in request.args:
            error_msg += f" - {request.args.get('error_description')}"

    code = request.args.get('code')
    if not code:
        error_msg = "No authorization code found in callback URL"

    # Validate state parameter matches session state if both exist
    state_param = request.args.get('state')
    session_state = session.get('oauth_state')
    if state_param and session_state and state_param != session_state:
        error_msg = "OAuth state parameter mismatch"

    if (error_msg):
        debug_info = {
            "has_oauth_state": 'oauth_state' in session,
            "request_args": dict(request.args)
        }
        print(f"OAuth Error: {error_msg} - Debug: {debug_info}")
        
        return {
            "error": "Authentication failed. Please try again.",
            "debug": debug_info
        }, 400

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
        ctfd_user.email = email
        
        # Preserve OAuth state temporarily during session clearing
        oauth_state_backup = session.get('oauth_state')
        session.clear()

        session['id'] = ctfd_user.id
        session['nonce'] = generate_nonce()
        session['hash'] = hmac(ctfd_user.password)
        session.permanent = True
        
        # Clean up OAuth state after successful authentication
        if oauth_state_backup:
            # OAuth flow completed successfully, state no longer needed
            pass
            
        clear_user_session(user_id=ctfd_user.id)

        db.session.commit()

        return redirect(f"{SERVER_DOMAIN}{ROUTE_PREFIX}")
    except AuthenticationError as e:
        db.session.rollback()

        import traceback
        traceback.print_exc()
        
        print(f"AuthenticationError during OAuth: {str(e)}")

        return {
            "error": "Authentication failed. Please try logging in again.",
            "debug": {
                "error_type": "AuthenticationError",
                "message": str(e)
            }
        }, 400
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

        import traceback
        traceback.print_exc()
        
        print(f"Unexpected error during OAuth at stage '{failure_stage}': {str(e)}")
        print(f"Debug info - Email: {email}, OAuth ID: {oauth_id}, Code: {code}")

        return {
            "error": "Something went wrong during login. Please try again.",
            "debug": {
                "failure_stage": failure_stage,
                "email": email,
                "oauth_id": oauth_id,
                "code": code
            }
        }, 500
    finally:
        db.session.close()