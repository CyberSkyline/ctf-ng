from __future__ import annotations

from collections.abc import Callable

from cyber_skyline.chall_parser.template import Template as ParserTemplate


from ...challenge.models import Challenge, Question
from ...challenge.utils import generate_seed
from functools import partial

def render_template(template: ParserTemplate, event_id: int, challenge_id: int, question_id: int, team_seed: str) -> str:
    result = template.eval(generate_seed(event_id, challenge_id, question_id, team_seed))
    return str(result) if result else ""

def resolve_environment_value(value: str | ParserTemplate, challenge: Challenge, variable_questions: dict[str, Question]):
    if isinstance(value, ParserTemplate):
        return partial(render_template, template=value, event_id=challenge.event_id, challenge_id=challenge.id, question_id=variable_questions[value.parent_variable].id)
    return value

def partial_environment(environment: dict[str, str | ParserTemplate] | list[str] | None, challenge: Challenge, variable_questions: dict[str, Question]) -> dict[str, str | Callable[[str], str]] | list[str] | None:
    if environment is None:
        return None

    if isinstance(environment, list):
        return environment

    return {k: resolve_environment_value(v, challenge, variable_questions) for k, v in environment.items() if v is not None}
