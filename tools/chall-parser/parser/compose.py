from typing import Literal, Any, Union, NewType, Dict
from attrs import define, field, validators
import re

from .service import Service
from .challenge_info import ChallengeInfo

@define
class Network:
    internal: Literal[True]

def validate_compose_name_pattern(instance, attribute, value):
    """Validator for compose resource names that must match ^[a-zA-Z0-9._-]+$"""
    if value is not None:
        pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        for key in value.keys():
            if not pattern.match(key):
                raise ValueError(f"Invalid {attribute.name} key '{key}': must match pattern ^[a-zA-Z0-9._-]+$")

# Custom types for pattern-validated dictionaries
ComposeResourceName = NewType('ComposeResourceName', str)
ServicesDict = Dict[ComposeResourceName, Service]
NetworksDict = Dict[ComposeResourceName, Network]

@define
class ComposeFile:
    # Challenge extension
    challenge: ChallengeInfo

    # Core sections with pattern validation and type hints
    services: ServicesDict = field(
        default=None, 
        validator=validators.optional(validate_compose_name_pattern)
    )
    networks: NetworksDict | None = field(
        default=None,
        validator=validators.optional(validate_compose_name_pattern)
    )
    
