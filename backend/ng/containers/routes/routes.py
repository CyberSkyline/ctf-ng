from flask_restx import Namespace, Resource
from ..controllers.start_containers import start_containers

from ...core.utils import (
    error_response,
    success_response,
)

from ...core.middleware import (
    user_endpoint,
)

container_namespace = Namespace("containers", description="containers")

@container_namespace.route("/<int:challenge_id>/start")
@container_namespace.param("challenge_id", "Challenge ID")
class ImportChallenge(Resource):
    @container_namespace.doc(
        description="Start a challenges containers",
        params={"challenge_id": "Challenge id to start containers for"},
        responses={
            200: "Sucess",
            400: "Bad request",
        },
    )
    def get(self, **kwargs):
        res = start_containers(kwargs["challenge_id"], 1, 1)
        return success_response({ "started": res })


@container_namespace.route("/<int:user_id>/vnc")
@contianer_namespace.param("user_id", "User Id")
class VncForward(Resource):
    @container_namespace.doc(
        description="Forward no vnc info to nginx. This should only be called by nginx",
        params={"user_id": "User id for user's vnc instance"},
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
