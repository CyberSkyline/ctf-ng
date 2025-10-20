from __future__ import annotations
from typing import Any

from cyber_skyline.chall_parser.template import Template as ParserTemplate

from ...challenge.models import Challenge, Question
from ...challenge.utils import generate_seed

class EnvVarRenderer:
    def __init__(self, event_id: int, challenge_id: int, question_id: int, template: ParserTemplate):
        self.event_id = event_id
        self.challenge_id = challenge_id
        self.question_id = question_id
        self.template = template

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "challenge_id": self.challenge_id,
            "question_id": self.question_id,
            "template": self.template.eval_str,
        }

    def __call__(self, team_seed: str) -> str:
        result = self.template.eval(generate_seed(self.event_id, self.challenge_id, self.question_id, team_seed))
        return str(result) if result else ""

def resolve_environment_value(value: str | ParserTemplate, challenge: Challenge, variable_questions: dict[str, Question]):
    if isinstance(value, ParserTemplate):
        return EnvVarRenderer(event_id=challenge.event_id, challenge_id=challenge.id, question_id=variable_questions[value.parent_variable].id, template=value)
    return value

def partial_environment(environment: dict[str, str | ParserTemplate] | list[str] | None, challenge: Challenge, variable_questions: dict[str, Question]) -> dict[str, str | EnvVarRenderer] | list[str] | None:
    if environment is None:
        return None

    if isinstance(environment, list):
        return environment

    return {k: resolve_environment_value(v, challenge, variable_questions) for k, v in environment.items() if v is not None}
