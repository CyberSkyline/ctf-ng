# backend/ng/user/routes.py
from flask_restx import Namespace, Resource
from ..controllers.authenticate import okta_login, okta_callback
from ..controllers.session_debug import session_status
from ...core.middleware import (
    public_endpoint,
)

oauth_namespace = Namespace("authenticate", description="Okta OAuth routes")

@oauth_namespace.route("/okta/login")
class OktaLogin(Resource):
    @public_endpoint()
    def get(self):
        return okta_login()

@oauth_namespace.route("/okta/callback")
class OktaCallback(Resource):
    @public_endpoint()
    def get(self):
        return okta_callback()

@oauth_namespace.route("/session/status")
class SessionStatus(Resource):
    @public_endpoint()
    def get(self):
        """Debug endpoint to check session state for OAuth troubleshooting"""
        return session_status()