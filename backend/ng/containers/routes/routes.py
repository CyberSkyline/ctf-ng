from flask_restx import Namespace, Resource
from ..controllers.vnc import forward_vnc

from ...core.utils import (
    success_response,
)

from ...core.middleware import (
    user_endpoint,
)

container_namespace = Namespace("containers", description="containers")

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
