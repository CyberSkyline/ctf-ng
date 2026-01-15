from datetime import datetime
from flask_restx import Namespace, Resource
from ..controllers.vnc import forward_vnc
from ..controllers.get_current_connected_challenge import get_current_connected_challenge
from ...core import BusinessLogicError
from ..models.IndvidualContainer import IndvidualContainer
from ...core.utils.rate_limit import limiter


from ...core.middleware import (
    user_endpoint,
)

from ...core.utils import (
    success_response,
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


@container_namespace.route("/me/restart")
class WorkspaceRestart(Resource):
    @container_namespace.doc(
        description="Restart users workspace",
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @limiter.limit("1 per 5 minutes")
    @user_endpoint()
    def post(self, current_user):
        teams = current_user.get_teams()
        now = datetime.utcnow()
        # Checks if user is in an event they can activley participate in
        team_stats = [
            tm.start_timestamp is not None and ((tm.end_time is not None and tm.end_time > now) or tm.end_time is None) for tm in teams
        ]
        if True in team_stats:
            ctr = IndvidualContainer.get_user_indvidual_container(current_user.id)
            ctr.restart()
            return success_response(True)
        else:
            raise BusinessLogicError("Must be apart of an active event to restart your workspace")
