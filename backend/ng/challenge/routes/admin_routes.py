from flask_restx import Namespace, Resource
import multiprocessing

from ...core.middleware.loaders.load_challenge import load_challenge
from ...core.middleware.loaders._util import LoaderType
from ...core.middleware.auth import admin_endpoint
from ...core.utils.api import success_response
from ..models import Challenge

from ...core.utils.emitters import emit_to_user

from ...challenge.models.ContainerBlueprint import ContainerBlueprint

challenge_admin_namespace = Namespace("/admin/challenges", description="challenge management")


@challenge_admin_namespace.route("")
class ChallengeList(Resource):
    @admin_endpoint()
    def get(self, **kwargs):
        """
        Get all challenges
        """
        challenges = Challenge.get_all_challenges()
        return success_response(challenges)

@challenge_admin_namespace.route("/<int:challenge_id>")
class ChallengeDetail(Resource):
    @admin_endpoint()
    @load_challenge(source = LoaderType.PARAM)
    def get(self, challenge, **kwargs):
        """
        Get detailed information about a specific challenge
        """
        return success_response(challenge)

@challenge_admin_namespace.route("/<int:challenge_id>/questions")
class ChallengeQuestions(Resource):
    @admin_endpoint()
    @load_challenge(source = LoaderType.PARAM)
    def get(self, challenge, **kwargs):
        """
        Get all questions for a specific challenge, including unrendered answer fields
        """
        return success_response(challenge.questions)

@challenge_admin_namespace.route("/<int:challenge_id>/hints")
class ChallengeHints(Resource):
    @admin_endpoint()
    @load_challenge(source = LoaderType.PARAM)
    def get(self, challenge, **kwargs):
        """
        Get all hints for a specific challenge, including all hint bodies
        """
        return success_response(challenge.hints)

@challenge_admin_namespace.route("/<int:challenge_id>/blueprints")
class ChallengeBlueprints(Resource):
    @admin_endpoint()
    @load_challenge(source = LoaderType.PARAM)
    def get(self, challenge: Challenge, **kwargs):
        """
        Get all container blueprints for a specific challenge
        """
        from ..models import ContainerBlueprint

        blueprints = ContainerBlueprint.query.filter_by(challenge_id=challenge.id).all()

        return success_response(blueprints)

@challenge_admin_namespace.route("/<int:challenge_id>/attempts")
class ChallengeAttempts(Resource):
    @admin_endpoint()
    @load_challenge(source = LoaderType.PARAM)
    def get(self, challenge: Challenge, **kwargs):
        """
        Get all attempts made for a challenge
        """
        from ...scoring.models import Attempt

        attempts = Attempt.query.filter_by(challenge_id=challenge.id).all()

        return success_response(attempts)

@challenge_admin_namespace.route("/<int:challenge_id>/pull")
class PullImages(Resource):
    @challenge_admin_namespace.doc(
        description="Pull all container images for a given challenge, Status of images returned via websockets",
        responses={
            200: "Success - Returns true",
            404: "Not found - Event does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    @admin_endpoint()
    @load_challenge(source=LoaderType.PARAM)
    def post(self, challenge: Challenge, current_user, **kwargs):
        blueprints = ContainerBlueprint.get_for_challenge(challenge.id)
        for blueprint in blueprints:
            # Will emit a websocket event to the user
            # On pull or fail
            def background_task(blueprint, current_user):
                try:
                    blueprint.pull_image()
                    emit_to_user(
                        "pull-success",
                        { "id" : blueprint.id, "image": blueprint.image },
                        current_user.id
                    )
                except Exception as err:
                    emit_to_user("pull-fail", {"error": str(err)}, current_user.id)


            proc = multiprocessing.Process(target=background_task, args=(blueprint, current_user))
            proc.start()

        return success_response(True)
