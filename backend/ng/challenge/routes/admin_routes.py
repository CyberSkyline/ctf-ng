from flask_restx import Namespace, Resource

from ...core.middleware import (
    admin_endpoint,
)
from ...core.utils import success_response
from ..controllers.import_challenge_from_yaml import import_challenge_from_yaml

challenge_admin_namespace = Namespace("challenges", description="challenge managment")

# /admin/events/event_id/import


@challenge_admin_namespace.route("/import")
class ImportChallenge(Resource):
    @challenge_admin_namespace.doc(
        description="Import a ng yaml definition",
        responses={
            200: "Success",
            400: "Bad request",
        },
    )
    @admin_endpoint(json_required=True)
    def post(self, json_data):
        challenge = import_challenge_from_yaml(json_data)
        return success_response(challenge)
