# backend/ng/user/routes.py
from flask_restx import Namespace, Resource

from ...core.middleware import (
    public_endpoint,
)
from ..controllers.authenticate import okta_callback, okta_login, okta_register, okta_register_card

oauth_namespace = Namespace("authenticate", description="Okta OAuth routes")

@oauth_namespace.route("/okta/login")
class OktaLogin(Resource):
    @public_endpoint()
    def get(self):
        return okta_login()

@oauth_namespace.route("/okta/register")
class OktaRegister(Resource):
    @public_endpoint()
    def get(self):
        return okta_register()

@oauth_namespace.route("/okta/register/card")
class OktaRegisterCard(Resource):
    @public_endpoint()
    def get(self):
        return okta_register_card()

@oauth_namespace.route("/okta/callback")
class OktaCallback(Resource):
    @public_endpoint()
    def get(self):
        return okta_callback()