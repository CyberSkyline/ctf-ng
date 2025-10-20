from flask_restx import Namespace, Resource

from ...core.middleware.loaders.load_challenge import load_challenge
from ...core.middleware.loaders.load_team_by_user_and_challenge import load_team_by_user_and_challenge
from ...core.middleware.loaders._util import LoaderType
from ...core.middleware.permission_middleware import check_permissions
from ...permissions.models.enums import PermissionEnum
from ...team.models.Team import Team
from ...user.models.User import User
from ...core.middleware.auth import user_endpoint
from ...core.utils.api import success_response
from ..models import Challenge


from ...containers.controllers.start_containers import start_containers
from ...containers.controllers.reboot_containers import reboot_containers
from ...containers.controllers.recycle_containers import recycle_containers

challenge_namespace = Namespace("challenges", description="challenge management")


@challenge_namespace.route("/<int:challenge_id>")
class EventChallengeRender(Resource):
    @user_endpoint()
    @load_challenge(source = LoaderType.PARAM)
    @load_team_by_user_and_challenge()
    @check_permissions(PermissionEnum.CAN_VIEW_CHALLENGES, "You do not have permission to view challenges.")
    @challenge_namespace.doc(
        description="Render a challenge for the user's team in the event.",
        responses={
            200: "Success",
            404: "Challenge or Event not found",
        },
    )
    def get(self, challenge_id: int, challenge: Challenge, team: Team, permissions, **kwargs):

        return success_response(challenge.render(team))


@challenge_namespace.route(
    "/<int:challenge_id>/containers"
)
class EventChallengeStartContainers(Resource):
    @user_endpoint()
    @load_challenge(source=LoaderType.PARAM)
    @load_team_by_user_and_challenge()
    @check_permissions(PermissionEnum.CAN_PLAY_CHALLENGES, "You do not have permission to play challenges.")
    @challenge_namespace.doc(
        description="Start a challenges containers",
        params={
            "event_id": "Event id challenge is in",
            "challenge_id": "Challenge id to start containers for",
        },
        responses={
            200: "Sucess",
            400: "Bad request",
        },
    )
    def post(self, team: Team, current_user: User, challenge_id: int, permissions):
        started = start_containers(challenge_id, team.id, current_user)
        return success_response(started)

@challenge_namespace.route("/<int:challenge_id>/containers/restart")
class EventChallengeRestartContainers(Resource):
    @challenge_namespace.doc(
        description="Reboot a challenges containers",
        params={
            "event_id": "Event id challenge is in",
            "challenge_id": "Challenge id to reboot containers for",
        },
        responses={
            200: "Sucess",
            400: "Bad request",
        },
    )
    @user_endpoint()
    @load_challenge(source=LoaderType.PARAM)
    @load_team_by_user_and_challenge()
    def post(self, team: Team, current_user: User, challenge_id: int, permissions):
        started = reboot_containers(challenge_id, team.id, current_user)
        return success_response(started)

@challenge_namespace.route("/<int:challenge_id>/containers/recycle")
class EventChallengeRecycleContainers(Resource):
    @challenge_namespace.doc(
        description="Recycle a challenges containers",
        params={
            "event_id": "Event id challenge is in",
            "challenge_id": "Challenge id to recycle containers for",
        },
        responses={
            200: "Sucess",
            400: "Bad request",
        },
    )
    @user_endpoint()
    @load_challenge(source=LoaderType.PARAM)
    @load_team_by_user_and_challenge()
    def post(self, team: Team, current_user: User, challenge_id: int, permissions):
        started = recycle_containers(challenge_id, team.id, current_user)
        return success_response(started)