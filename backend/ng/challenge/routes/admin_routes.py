from ...core.middleware.loaders.load_challenge import load_challenge
from ...core.middleware.loaders._util import LoaderType
from ...core.middleware.auth import admin_endpoint
from ...core.utils.api import success_response
from ..models import Challenge

from flask_restx import Namespace, Resource

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


