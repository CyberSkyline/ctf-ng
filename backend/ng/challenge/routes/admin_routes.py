import base64
from typing import Any
from flask_restx import Namespace, Resource
import multiprocessing

from ..controllers.admin import import_challenge_from_yaml, update_challenge_from_yaml, lint_challenge
from ..models import Challenge, ContainerBlueprint
from ...core.middleware.loaders import load_event, load_challenge
from ...core.middleware.loaders._util import LoaderType
from ...core.middleware.auth import admin_endpoint
from ...core.utils.api import success_response
from ...core.utils.emitters import emit_to_user
from ...event.models import Event

challenge_admin_namespace = Namespace("/admin/challenges", description="challenge management")

@challenge_admin_namespace.route("")
class ChallengeList(Resource): # Feels like I should rename this but I'm not sure what I should rename it too
    @admin_endpoint()
    def get(self, **kwargs):
        """
        Get all challenges
        """
        challenges = Challenge.get_all_challenges()
        return success_response(challenges)


    @challenge_admin_namespace.doc(
        description="Create a challenge for an event using YAML configuration",
        params={
            "yaml": {
                "description": "YAML representation of the challenge",
                "in": "body",
                "required": True,
                "type": "string",
            },
            "event_id": {
                "description": "ID of the event to associate the challenge with",
                "in": "query",
                "required": True,
                "type": "integer",
            }
        },
        responses={
            200: "Success - Challenge created successfully",
            400: "Bad request - Invalid challenge data",
            404: "Not found - Event does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    @admin_endpoint(json_required=True)
    @load_event(source = LoaderType.BODY)
    def post(self, event: Event, json_data, **kwargs):
        """
        Create a new challenge from YAML.
        """
        payload = base64.urlsafe_b64decode(json_data["yaml"]).decode("utf-8")
        challenge = import_challenge_from_yaml(event, payload)
        return success_response(challenge)

class ChallengeLint(Resource):
    @challenge_admin_namespace.doc(
        description="Lint a challenge YAML configuration without creating the challenge",
        params={
            "yaml": {
                "description": "YAML representation of the challenge",
                "in": "body",
                "required": True,
                "type": "string",
            }
        },
        responses={
            200: "Success - YAML is valid",
            400: "Bad request - Invalid YAML format",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    @admin_endpoint(json_required=True)
    def post(self, json_data, **kwargs):
        """
        Lint a challenge YAML configuration.
        """
        payload = base64.urlsafe_b64decode(json_data["yaml"]).decode("utf-8")
        # Just attempt to parse the YAML to see if it's valid
        return success_response(lint_challenge(payload))


@challenge_admin_namespace.route("/<int:challenge_id>")
class ChallengeDetail(Resource):
    @admin_endpoint()
    @load_challenge(source = LoaderType.PARAM)
    def get(self, challenge, **kwargs):
        """
        Get detailed information about a specific challenge
        """
        return success_response(challenge)

    @admin_endpoint(json_required=True)
    @load_challenge(source = LoaderType.PARAM)
    def put(self, challenge: Challenge, json_data, **kwargs):
        """
        Update a specific challenge from YAML.
        """
        payload = base64.urlsafe_b64decode(json_data["yaml"]).decode("utf-8")
        updated_challenge = update_challenge_from_yaml(challenge, payload)
        return success_response(updated_challenge)

@challenge_admin_namespace.route("/<int:challenge_id>/yaml")
class ChallengeYAML(Resource):
    @admin_endpoint()
    @load_challenge(source = LoaderType.PARAM)
    def get(self, challenge: Challenge, **kwargs):
        """
        Get the YAML representation of a specific challenge
        """
        yaml_data = challenge.yaml.body
        return success_response({"yaml": yaml_data})

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
