from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from CTFd.models import db
from cyber_skyline.chall_parser.compose.answer import Answer
from cyber_skyline.chall_parser.compose.challenge_info import TextBody
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string

from ng.challenge.models import ChallengeVariable

from ....challenge.models import Challenge, ChallengeTag, ContainerBlueprint, Hint, Question
from ....core.exceptions import ValidationError

if TYPE_CHECKING:
    from ....event.models.Event import Event

# TODO: Will this handle updating challenges as well?

def import_challenge_from_yaml(event: Event, json_data) -> Challenge:
    """
    Import a challenge from a YAML definition.
    :return: The imported challenge.
    """
    payload = base64.urlsafe_b64decode(json_data["yaml"])

    try:
        compose_file = parse_compose_string(payload.decode("utf-8"))
    except Exception as e:
        print(e)
        raise ValidationError(f"Invalid YAML format: {e}") from e

    try:
        challenge_info = compose_file.challenge
        challenge = Challenge.create_challenge(
            event_id=event.id,
            name=challenge_info.name,
            icon=challenge_info.icon,
            description=challenge_info.description,
            summary=challenge_info.summary,
            commit=False,
        )

        hints = compose_file.challenge.hints or []
        tags = compose_file.challenge.tags or []
        questions = compose_file.challenge.questions or []
        services = compose_file.services or {}
        variables = compose_file.challenge.variables or {}
        db_variables: dict[str, ChallengeVariable] = {}

        for hint in hints:
            Hint.create_hint(
                challenge_id=challenge.id,
                body=hint.body.content if isinstance(hint.body, TextBody) else hint.body,
                preview=hint.preview,
                deduction=hint.deduction,
                commit=False,
            )

        for tag in tags:
            ChallengeTag.create_tag(
                challenge_id=challenge.id,
                name=tag,
                commit=False,
            )

        for (key, variable) in variables.items():
            db_variables[key] = ChallengeVariable.create_variable(
                challenge_id=challenge.id,
                name=key,
                default=variable.default,
                template=variable.template.eval_str,
                commit=False,
            )

        for question in questions:
            question_payload = {
                "challenge_id": challenge.id,
                "name": question.name,
                "body": question.body,
                "points": question.points,
                "placeholder": question.placeholder,
                "max_attempts": question.max_attempts,
            }

            # Answer is regular string
            if isinstance(question.answer, str):
                question_payload["answer"] = question.answer

            # Answer has test cases
            elif isinstance(question.answer, Answer):
                question_payload["answer"] = question.answer.body
                test_cases = question.answer.test_cases or []
                for test_case in test_cases: # noqa B007
                    # TODO - create test cases
                    # Do test cases need to be updated or
                    # can we just throw them out and restart
                    pass
            # Answer uses a template
            else:
                variable = db_variables.get(question.answer.parent_variable)
                question_payload["template"] = True
                question_payload["answer"] = "TODO - IMPLEMENT"
                pass

            Question.create_question(**question_payload, commit=False)

        for service in services.items():
            service_data = service[1]

            # TODO: Handle templates in environment
            payload = {
                "challenge_id": challenge.id,
                "image": service_data.image,
                "hostname": service_data.hostname,
                "stdin_open": service_data.stdin_open,
                "tty": service_data.tty,
                "entrypoint": service_data.entrypoint,
                "environment": service_data.environment,
                "networks": service_data.networks,
                "cap_add": service_data.cap_add,
                "mem_limit": service_data.mem_limit,
                "memswap_limit": service_data.memswap_limit,
                "cpus": service_data.cpus,
                "user": service_data.user,
            }
            ContainerBlueprint.create_container_blueprint(
                **payload,
                commit=False,
            )

        db.session.commit()
        return challenge
    except Exception as e:
        db.session.rollback()
        raise e
