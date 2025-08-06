from flask_restx import Namespace, Resource
from ..controllers.vnc import forward_vnc
from ..controllers.get_current_connected_challenge import get_current_connected_challenge
from ..models.ContainerInstance import ContainerInstance


from ...core.middleware import (
    user_endpoint,
)

container_namespace = Namespace("containers", description="containers")

@container_namespace.route("/vnc")
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

@container_namespace.route("/me/current_challenge")
class GetCurrentChallenge(Resource):
    @container_namespace.doc(
        description="Get Current Challenge ID user is connected to. Returns null if not connected",
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @user_endpoint()
    def get(self, current_user):
        current_chall = get_current_connected_challenge(current_user.id)
        return success_response(current_chall)
