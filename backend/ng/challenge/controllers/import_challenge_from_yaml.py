import base64

from attrs import asdict
from CTFd.models import db
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string

from ...core.exceptions import ValidationError
from ..models.Challenge import Challenge
from ..models.ChallengeTag import ChallengeTag
from ..models.ContainerBlueprint import ContainerBlueprint
from ..models.Hint import Hint
from ..models.Question import Question


def import_challenge_from_yaml(json_data) -> Challenge:
    """
    Import a challenge from a YAML definition.
    :return: The imported challenge.
    """
    payload = base64.urlsafe_b64decode(json_data["yaml"])

    try:
        yaml = asdict(parse_compose_string(payload.decode("utf-8")), filter=lambda y, x: x is not None)
    except Exception as e:
        print(e)
        raise ValidationError(f"Invalid YAML format: {e}") from e

    try:
        challenge_yaml = yaml["challenge"]
        challenge = Challenge.create_challenge(
            name=challenge_yaml["name"],
            icon=challenge_yaml["icon"],
            description=challenge_yaml["description"],
            summary=challenge_yaml["summary"],
            commit=False,
        )

        for hint in challenge_yaml["hints"]:
            Hint.create_hint(challenge_id=challenge.id, **hint, commit=False)

        for tag in challenge_yaml["tags"]:
            ChallengeTag.create_tag(challenge_id=challenge.id, name=tag, commit=False)

        for question in challenge_yaml["questions"]:
            Question.create_question(challenge_id=challenge.id, **question, commit=False)

        services_yaml = yaml["services"]
        for blueprint in services_yaml.items():
            ContainerBlueprint.create_container_blueprint(challenge_id=challenge.id, **blueprint[1], commit=False)

        db.session.commit()
        return challenge
    except Exception as e:
        db.session.rollback()
        raise e
