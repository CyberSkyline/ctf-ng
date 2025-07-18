from flask_restx import Namespace, Resource
from ..controllers.start_containers import start_containers
from ..controllers.vnc import forward_vnc

from ...core.utils import (
    success_response,
)

from ...core.middleware import (
    user_endpoint,
)

container_namespace = Namespace("containers", description="containers")

# I will more than likely move this.
# Once we have a better idea of the route path for events/challenges
# Currently this works though
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
    @user_endpoint()
    def get(self, current_user, **kwargs):
        ## Team id is currently hardcoded
        ## I couldn't find any middleware for getting the user's current team
        ## Again this should be a pretty simple fix
        res = start_containers(kwargs["challenge_id"], 2, current_user)
        return success_response({ "started": res })


@container_namespace.route("/vnc")
@container_namespace.param("user_id", "User Id")
class VncForward(Resource):
    @container_namespace.doc(
        description="Forward no vnc info to nginx. This should only be called by nginx",
        params={"user_id": "User id for user's vnc instance"},
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @user_endpoint()
    def get(self, current_user):
        return forward_vnc(current_user.id)
