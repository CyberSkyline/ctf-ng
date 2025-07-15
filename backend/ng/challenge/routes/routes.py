import base64
from typing import cast

from attrs import asdict
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string
from flask_restx import Namespace, Resource

from ...core.middleware import (
    admin_endpoint,
)
from ..models.Challenge import Challenge, ChallengeYaml

challenge_admin_namespace = Namespace("challenges", description="challenge managment")


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
        payload = base64.urlsafe_b64decode(json_data["yaml"])

        try:
            parsed_yaml = asdict(parse_compose_string(payload.decode("utf-8")), filter=lambda y, x: x is not None)
            return Challenge.create_from_yaml(yaml=cast(ChallengeYaml, parsed_yaml))
        except Exception as e:
            print(f"Error parsing YAML: {e}")
            return {"error": "Invalid YAML format"}, 400
