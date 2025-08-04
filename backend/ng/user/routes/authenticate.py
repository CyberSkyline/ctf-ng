from flask import Blueprint
from flask_restx import Api, Namespace, Resource
from ..controllers.authenticate import okta_login, okta_callback

oauth_namespace = Namespace("authenticate", description="Okta OAuth routes")

@oauth_namespace.route("/okta/login")
class OktaLogin(Resource):
    def get(self):
        return okta_login()

@oauth_namespace.route("/okta/callback")
class OktaCallback(Resource):
    def get(self):
        return okta_callback()