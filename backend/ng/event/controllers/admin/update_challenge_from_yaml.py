from __future__ import annotations

import base64
from typing import Any

from CTFd.models import db
from cyber_skyline.chall_parser.compose.answer import Answer as ParserAnswer
from cyber_skyline.chall_parser.compose.challenge_info import TextBody
from cyber_skyline.chall_parser.template import Template as ParserTemplate
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string

from ...utils.challenge_yaml import partial_environment
from ....challenge.models import Challenge, ChallengeTag, ContainerBlueprint, Hint, Question, ChallengeVariable
from ....core.exceptions import ValidationError

def update_challenge_from_yaml(challenge_id: int, json_data: dict[str, Any]) -> Challenge:
    payload = base64.urlsafe_b64decode(json_data["yaml"])
    challenge: Challenge | None = Challenge.query.get(challenge_id)

    if not challenge:
        raise ValidationError(f"Challenge with ID {challenge_id} does not exist.")

    try:
        compose_file = parse_compose_string(payload.decode("utf-8"))
    except Exception as e:
        print(e)
        raise ValidationError(f"Invalid YAML format: {e}") from e

    try:
        uploaded_challenge = compose_file.challenge

        challenge.name = uploaded_challenge.name
        challenge.icon = uploaded_challenge.icon
        challenge.description = uploaded_challenge.description
        challenge.summary = uploaded_challenge.summary

        if not challenge.yaml:
            raise ValidationError(f"Challenge YAML for challenge ID {challenge.id} does not exist.")
        challenge.yaml.body = payload.decode("utf-8")

        hints = {hint.name: hint for hint in challenge.hints}
        uploaded_hints = {h.name: h for h in uploaded_challenge.hints or []}
        if len(set(hints.keys()) - set(uploaded_hints.keys())) > 0:
            raise ValidationError("Cannot remove existing hints when updating a challenge.")

        for hint in uploaded_challenge.hints or []:
            if hint.name in hints:
                existing_hint = hints[hint.name]
                existing_hint.body = hint.body.content if isinstance(hint.body, TextBody) else hint.body
                existing_hint.preview = hint.preview
                existing_hint.deduction = hint.deduction
            else:
                Hint.create_hint(
                    name=hint.name,
                    challenge_id=challenge.id,
                    body=hint.body.content if isinstance(hint.body, TextBody) else hint.body,
                    preview=hint.preview,
                    deduction=hint.deduction,
                    commit=False,
                )

        tags = {tag.name: tag for tag in challenge.tags}
        uploaded_tags = set(uploaded_challenge.tags or {})
        for tag in set(tags.keys()) - uploaded_tags:
            db.session.delete(tags[tag])

        for tag in uploaded_challenge.tags or []:
            if tag not in tags:
                ChallengeTag.create_tag(
                    challenge_id=challenge.id,
                    name=tag,
                    commit=False,
                )

        variables = {var.name: var for var in challenge.variables}
        if uploaded_challenge.variables is not None:
            uploaded_variables = set(uploaded_challenge.variables.keys() or {})
            for var in set(variables.keys()) - uploaded_variables:
                db.session.delete(variables[var])

            for (key, variable) in (compose_file.challenge.variables or {}).items():
                if key in variables:
                    existing_var = variables[key]
                    existing_var.default = variable.default
                    existing_var.template = variable.template.eval_str
                else:
                    variables[key] = ChallengeVariable.create_variable(
                        challenge_id=challenge.id,
                        name=key,
                        default=variable.default,
                        template=variable.template.eval_str,
                        commit=False,
                    )

        questions: dict[str, Question] = {question.name: question for question in challenge.questions}
        uploaded_questions = {q.name: q for q in uploaded_challenge.questions or []}
        if len(set(questions.keys()) - set(uploaded_questions.keys())) > 0:
            raise ValidationError("Cannot remove existing questions when updating a challenge.")
        db_variable_questions: dict[str, Question] = {}
        for question in uploaded_challenge.questions or []:
            if question.name in questions:
                existing_question = questions[question.name]
                existing_question.body = question.body
                if isinstance(question.answer, str):
                    existing_question.answer = question.answer
                elif isinstance(question.answer, ParserAnswer):
                    existing_question.answer = question.answer.body
                else:
                    variable = variables.get(question.answer.parent_variable)
                    if variable:
                        existing_question.answer_variable_id = variable.id
                    else:
                        raise ValidationError(f"Variable {question.answer.parent_variable} not found for question {question.name}")
                    db_variable_questions[question.answer.parent_variable] = existing_question
                existing_question.max_attempts = question.max_attempts
                existing_question.points = question.points
            else:
                new_answer = None
                new_answer_variable_id = None
                if isinstance(question.answer, str):
                    new_answer = question.answer
                elif isinstance(question.answer, ParserAnswer):
                    new_answer = question.answer.body
                else:
                    variable = variables.get(question.answer.parent_variable)
                    if variable:
                        new_answer_variable_id = variable.id
                    else:
                        raise ValidationError(f"Variable {question.answer.parent_variable} does not exist but is used in {question.name}")

                db_question = Question.create_question(
                    challenge_id=challenge.id,
                    name=question.name,
                    body=question.body,
                    points=question.points,
                    placeholder=question.placeholder,
                    max_attempts=question.max_attempts,
                    answer=new_answer,
                    answer_variable_id=new_answer_variable_id,
                    commit=False,
                )

                if isinstance(question.answer, ParserTemplate):
                    db_variable_questions[question.answer.parent_variable] = db_question

        blueprints = {blueprint.hostname: blueprint for blueprint in challenge.blueprints}
        if compose_file.services:
            for (service_name, service_data) in compose_file.services.items():
                if service_name in blueprints:
                    existing_blueprint = blueprints[service_name]
                    existing_blueprint.image = service_data.image
                    existing_blueprint.hostname = service_data.hostname
                    existing_blueprint.stdin_open = service_data.stdin_open
                    existing_blueprint.tty = service_data.tty
                    existing_blueprint.command = service_data.command
                    existing_blueprint.entrypoint = service_data.entrypoint
                    existing_blueprint.environment = partial_environment(service_data.environment, challenge, db_variable_questions)
                    existing_blueprint.networks = service_data.networks
                    existing_blueprint.cap_add = service_data.cap_add
                    existing_blueprint.mem_limit = service_data.mem_limit
                    existing_blueprint.memswap_limit = service_data.memswap_limit
                    existing_blueprint.cpus = float(service_data.cpus) if service_data.cpus else None
                    existing_blueprint.user = service_data.user
                else:
                    ContainerBlueprint.create_container_blueprint(
                        challenge_id=challenge.id,
                        image=service_data.image,
                        hostname=service_data.hostname,
                        stdin_open=service_data.stdin_open,
                        tty=service_data.tty,
                        command=service_data.command,
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

        return (challenge)
    except Exception as e:
        db.session.rollback()
        raise e