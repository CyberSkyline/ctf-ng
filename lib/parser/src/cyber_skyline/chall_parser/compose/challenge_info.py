from typing import Literal
from attrs import define, field

from ..rewriter import Template
from .validators import validate_tabler_icon, validate_template_evals


@define
class Question:
    """Represents a single question in the challenge.
    
    Each question defines what the player needs to answer and how many points it's worth.
    """
    name: str  # Developer facing name for the question (e.g., "flag", "password")
    question: str  # The actual question text presented to players
    points: int  # Point value for correctly answering this question (e.g., 10, 100)
    answer: str  # The correct answer (can be a regex pattern)
    max_attempts: int  # Maximum number of attempts allowed (e.g., 20)

@define
class TextHint:
    """A text-based hint for players."""
    type: Literal['text']
    content: str  # The actual hint text content

# @define
# class ImageHint:
#     type: Literal['image']
#     source: str

@define
class Hint:
    """A hint that players can open to get help solving the challenge.
    
    Hints can be either structured (TextHint) or simple strings.
    Each hint has a preview and costs points when opened.
    """
    hint: TextHint | str  # The hint content - can be structured or simple text, may in the future support more complex hint types
    preview: str  # Short preview text shown before opening the hint
    deduction: int  # Points deducted when this hint is opened (e.g., 10)

@define
class Variable:
    """Template variable that can be randomized for each challenge instance.
    
    Variables use the Faker library for generation and can be referenced
    throughout the compose file using YAML anchors and aliases.
    """
    template: Template = field(validator=validate_template_evals)
                       # Python code fragment using Faker library functions
                       # e.g., "fake.bothify('SKY-????-####', letters=string.ascii_uppercase)"
    default: str  # Default value with YAML anchor for referencing elsewhere
                 # This anchor can be used in services like: environment: VARIABLE1: *var1

@define
class ChallengeInfo:
    """Container for all challenge development information.
    
    This is the main x-challenge block that defines everything about the CTF challenge.
    """
    # Required fields
    name: str  # Name of the challenge
    description: str  # The description presented to players
    questions: list[Question]  # List of questions players must answer
    
    # Optional fields
    icon: str | None = field(
        default=None, 
        validator=validate_tabler_icon
    )  # Tabler icon name (validated against known icons)
    hints: list[Hint] | None = None  # List of hints players can access
    summary: str | None = None  # Optional summary text
    
    # Template and variable system
    templates: dict[str, str] | None = None  # Centralized location for reusable templates
                                           # e.g., flag-tmpl: &flag_tmpl "fake.bothify('CTF{????-####}')"
    variables: dict[str, Variable] | None = None  # Variables for randomization
                                                 # You can name variables anything that's a valid YAML key
    
    # Categorization
    tags: list[str] | None = None  # Category tags (e.g., ["web", "easy"], ["crypto", "hard"])

# Usage example in compose file:
# x-challenge:
#   name: Web Challenge
#   description: Find the hidden flag
#   icon: globe
#   questions:
#     - name: flag
#       question: What is the flag?
#       points: 100
#       answer: CTF{.*}
#       max_attempts: 5
#   hints:
#     - hint: Check the environment variables
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