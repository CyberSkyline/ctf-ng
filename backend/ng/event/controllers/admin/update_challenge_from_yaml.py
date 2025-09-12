import base64
from typing import Any
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string

from ng.core.exceptions import ValidationError
from ....challenge.models import Challenge


def update_challenge_from_yaml(challenge_id: int, json_data: dict[str, Any]) -> None:
    payload = base64.urlsafe_b64decode(json_data["yaml"])

    try:
        compose_file = parse_compose_string(payload.decode("utf-8"))
    except Exception as e:
        print(e)
        raise ValidationError(f"Invalid YAML format: {e}") from e

    try:
        challenge_info = compose_file.challenge
        challenge: Challenge = Challenge.query.get(challenge_id)
        if not challenge:
            raise ValidationError(f"Challenge with ID {challenge_id} does not exist.")

        challenge.name = challenge_info.name
        challenge.icon = challenge_info.icon
        challenge.description = challenge_info.description
        challenge.summary = challenge_info.summary
        challenge.challenge_yaml = payload.decode("utf-8")

        hints = {hint.name: hint for hint in challenge.hints}
        tags = {tag.name for tag in challenge.tags}
        questions = {question.name: question for question in challenge.questions}
        blueprints = {blueprint.hostname: blueprint for blueprint in challenge.blueprints}
    except Exception as e:
        print(e)
        raise ValidationError(f"Invalid challenge data in YAML: {e}") from e