from __future__ import annotations

import base64
from typing import TYPE_CHECKING
from collections.abc import Callable

from CTFd.models import db
from cyber_skyline.chall_parser.compose.answer import Answer
from cyber_skyline.chall_parser.compose.challenge_info import TextBody
from cyber_skyline.chall_parser.template import Template
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string

from ....notifications.services import NotificationService
from ng.challenge.models import ChallengeVariable
from ....challenge.models import Challenge, ChallengeTag, ContainerBlueprint, Hint, Question
from ....challenge.utils import generate_seed
from ....core.exceptions import ValidationError
from functools import partial

if TYPE_CHECKING:
    from ....event.models.Event import Event

# TODO: Will this handle updating challenges as well?

def render_template(template: Template, event_id: int, challenge_id: int, question_id: int, team_seed: str) -> str:
    result = template.eval(generate_seed(event_id, challenge_id, question_id, team_seed))
    return str(result) if result else ""

def resolve_environment_value(value: str | Template, challenge: Challenge, question_id: int):
    if isinstance(value, Template):
        return partial(render_template, template=value, event_id=challenge.event_id, challenge_id=challenge.id, question_id=question_id)
    return value

def partial_environment(environment: dict[str, str | Template] | list[str] | None, challenge: Challenge, variable_questions: dict[str, Question]) -> dict[str, str | Callable[[str], str]] | list[str] | None:
    if environment is None:
        return None

    if isinstance(environment, list):
        return environment

    return {k: resolve_environment_value(v, challenge, variable_questions[k].id) for k, v in environment.items() if v is not None}


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
            challenge_yaml=payload.decode("utf-8"),
        )

        hints = compose_file.challenge.hints or []
        tags = compose_file.challenge.tags or []
        questions = compose_file.challenge.questions or []
        services = compose_file.services or {}
        variables = compose_file.challenge.variables or {}
        db_variables: dict[str, ChallengeVariable] = {}
        db_variable_questions: dict[str, Question] = {}

        for hint in hints:
            Hint.create_hint(
                name=hint.name,
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
            answer = None
            answer_variable_id = None

            # Answer is regular string
            if isinstance(question.answer, str):
                answer = question.answer
            # Answer has test cases
            elif isinstance(question.answer, Answer):
                answer = question.answer.body
                test_cases = question.answer.test_cases or []
                for test_case in test_cases: # noqa B007
                    # TODO - create test cases
                    # Do test cases need to be updated or
                    # can we just throw them out and restart
                    pass
            # Answer uses a template
            else:
                variable = db_variables.get(question.answer.parent_variable)
                answer_variable_id = variable.id if variable else None

            db_question = Question.create_question(
                challenge_id=challenge.id,
                name=question.name,
                body=question.body,
                points=question.points,
                placeholder=question.placeholder,
                max_attempts=question.max_attempts,
                answer=answer,
                answer_variable_id=answer_variable_id,
                commit=False
            )

            if isinstance(db_question.answer, Template):
                db_variable_questions[question.answer.parent_variable] = db_question

        for service_data in services.values():
            ContainerBlueprint.create_container_blueprint(
                challenge_id=challenge.id,
                image=service_data.image,
                hostname=service_data.hostname,
                stdin_open=service_data.stdin_open,
                tty=service_data.tty,
                entrypoint=service_data.entrypoint,
                environment=partial_environment(service_data.environment, challenge, db_variable_questions),
                networks=service_data.networks,
                cap_add=service_data.cap_add,
                mem_limit=service_data.mem_limit,
                memswap_limit=service_data.memswap_limit,
                cpus=float(service_data.cpus) if service_data.cpus else None,
                user=service_data.user,
                commit=False,
            )

        db.session.commit()

        NotificationService.notify_challenge_released(
            event_id=event.id,
            challenge_id=challenge.id,
            challenge_name=challenge.name,
        )

        return challenge
    except Exception as e:
        db.session.rollback()
        raise e
