# Copyright 2025 Cyber Skyline

# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the “Software”), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.
from typing import Literal
from attrs import define, field, validators as v
from cyber_skyline.chall_parser.compose.answer import Answer
from cyber_skyline.chall_parser.template import Template
import cyber_skyline.chall_parser.compose.validators as cv
@define
class Question:
    """Represents a single question in the challenge.
    
    Each question defines what the player needs to answer and how many points it's worth.
    """
    name: str = field(validator=v.instance_of(str))  # Developer facing name for the question (e.g., "flag", "password")
    body: str = field(validator=v.instance_of(str))  # The actual question text presented to players
    points: int = field(validator=v.instance_of(int))  # Point value for correctly answering this question (e.g., 10, 100)
    answer: str | Answer | Template = field(validator=cv.or_(
        v.and_(v.instance_of(str), cv.validate_regex),
        v.and_(v.instance_of(Answer), cv.validate_answer),
        v.instance_of(Template)
    ))  # The correct answer

    max_attempts: int = field(validator=v.instance_of(int))  # Maximum number of attempts allowed (e.g., 20)
    placeholder: str | None = field(default=None, validator=v.optional(v.instance_of(str)))  # Optional placeholder text for answer input fields (e.g., 'CTF{...}' or 'Enter your answer here')

@define
class TextBody:
    """A text-based hint for players."""
    type: Literal['text'] = field(validator=v.in_(['text']))
    content: str = field(validator=v.instance_of(str))  # The actual hint text content

# @define
# class ImageBody:
#     type: Literal['image']
#     source: str

@define
class Hint:
    """A hint that players can open to get help solving the challenge.
    
    Hints can be either structured (TextHint) or simple strings.
    Each hint has a preview and costs points when opened.
    """
    name: str = field(validator=v.instance_of(str))  # Developer facing name for the hint (e.g., "hint1", "hint2")
    body: TextBody | str = field(validator=cv.or_(
        v.instance_of(TextBody),
        v.instance_of(str)
    ))  # The hint content - can be structured or simple text, may in the future support more complex hint types
    preview: str = field(validator=v.instance_of(str))  # Short preview text shown before opening the hint
    deduction: int = field(validator=v.instance_of(int))  # Points deducted when this hint is opened (e.g., 10)

@define
class Variable:
    """Template variable that can be randomized for each challenge instance.
    
    Variables use the Faker library for generation and can be referenced
    throughout the compose file using YAML anchors and aliases.
    """
    template: Template = field(validator=cv.validate_template_evals)
                       # Python code fragment using Faker library functions
                       # e.g., "fake.bothify('SKY-????-####', letters=string.ascii_uppercase)"
    default: str = field(validator=v.instance_of(str))  # Default value with YAML anchor for referencing elsewhere
                 # This anchor can be used in services like: environment: VARIABLE1: *var1


def _sel_hint_name(hint: Hint) -> str:
    return hint.name

def _sel_question_name(question: Question) -> str:
    return question.name

@define
class ChallengeInfo:
    """Container for all challenge development information.
    
    This is the main x-challenge block that defines everything about the CTF challenge.
    """
    # Required fields
    name: str = field(validator=v.instance_of(str))  # Name of the challenge
    description: str = field(validator=v.instance_of(str))  # The description presented to players
    questions: list[Question] = field(validator=v.deep_iterable(v.instance_of(Question), v.and_(v.instance_of(list), cv.unique(_sel_question_name))))  # List of questions players must answer

    # Optional fields
    icon: str | None = field(
        default=None, 
        validator=cv.validate_tabler_icon
    )  # Tabler icon name (validated against known icons)
    hints: list[Hint] | None = field(
        default=None, validator=v.optional(v.deep_iterable(v.instance_of(Hint), v.and_(v.instance_of(list), cv.unique(_sel_hint_name)))))  # List of hints players can access
    summary: str | None = field(
        default=None, validator=v.optional(v.instance_of(str)))  # Optional summary text

    # Template and variable system
    templates: dict[str, str] | None = field(
        default=None, validator=v.optional(v.instance_of(dict)))  # Centralized location for reusable templates
                                           # e.g., flag-tmpl: &flag_tmpl "fake.bothify('CTF{????-####}')"
    variables: dict[str, Variable] | None = field(
        default=None, validator=v.optional(v.instance_of(dict)))  # Variables for randomization
                                                 # You can name variables anything that's a valid YAML key
    
    # Categorization
    tags: list[str] | None = field(
        default=None, validator=v.optional(v.deep_iterable(v.instance_of(str), v.instance_of(list))))  # Category tags (e.g., ["web", "easy"], ["crypto", "hard"])

# Usage example in compose file:
# x-challenge:
#   name: Web Challenge
#   description: Find the hidden flag
#   icon: globe
#   questions:
#     - name: flag
#       body: What is the flag?
#       points: 100
#       answer: CTF{.*}
#       max_attempts: 5
#   hints:
#     - name: hint1
#       body: Check the environment variables
#       preview: Look at env vars
#       deduction: 10
#   template:
#     flag-tmpl: &flag_tmpl "fake.bothify('CTF{????-####}')"
#   variables:
#     session_id:
#       template: "fake.uuid4()"
#       default: &session_var "default-session-id"
#   tags: ["web", "beginner"]
# 
# services:
#   web:
#     image: nginx
#     environment:
#       SESSION_ID: *session_var  # References the variable default value