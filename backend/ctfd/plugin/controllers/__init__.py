from flask import Blueprint
from flask_restx import Api, Namespace, Resource

api = Blueprint("plugin_api", __name__, url_prefix="/api/v1")

api_v1 = Api(api, version="1.0", doc="/")

test_namespace = Namespace("test", description="Test operations")

@test_namespace.route("")
class TestResource(Resource):
    def get(self):
        return {"message": "Hello from the test namespace!"}, 200


api_v1.add_namespace(test_namespace, path="/test")