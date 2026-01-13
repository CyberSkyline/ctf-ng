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
"""
Validation functions for CTF challenge configuration.

This module provides validators for ensuring that challenge configurations
use valid values, particularly for UI elements like icons.
"""

import logging
import re
import ipaddress
from typing import Any
from cyber_skyline.chall_parser.compose.answer import Answer, AnswerTestCase
from cyber_skyline.chall_parser.template import Template
from collections.abc import Callable, Container
from cyber_skyline.chall_parser.compose.types import ComposeResourceName


logger = logging.getLogger(__name__)

def is_ipv4(instance, attribute, value: str) -> None:
    """Validator to ensure a string is a valid IPv4 address.
    
    Args:
        instance: The instance being validated
        attribute: The attribute being validated
        value: The string value to validate as an IPv4 address
    Raises:
        ValueError: If the value is not a valid IPv4 address
    """
    try:
        ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError as e:
        raise ValueError(f"Value '{value}' for {attribute.name} is not a valid IPv4 address") from e

def contains[TValue](value: TValue) -> Callable[[Any, Any, Container[TValue]], None]:
    """Validator to ensure a container contains a specific value.
    
    Args:
        value: The value that must be present in the container
        
    Returns:
        A validator function
    """
    def validate(instance, attribute, container: Container[TValue]):
        if value not in container:
            raise ValueError(f"Container for {attribute.name} must contain value: {value}")
    return validate

def is_ipv4_cidr(instance, attribute, value: str) -> None:
    """Validator to ensure a string is a valid IPv4 CIDR notation.
    
    Args:
        instance: The instance being validated
        attribute: The attribute being validated
        value: The string value to validate as an IPv4 CIDR
    Raises:
        ValueError: If the value is not a valid IPv4 CIDR notation
    """
    try:
        ipaddress.IPv4Network(value, strict=False)
    except (ValueError, ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
        raise ValueError(f"Value '{value}' for {attribute.name} is not valid IPv4 CIDR notation") from e

def unique[TItem, TSelReturn](selector: Callable[[TItem], TSelReturn]) -> Callable[[Any, Any, list[Any]], None]:
    """Validator to ensure all items in a list are unique based on a selector function."""
    def validate(instance, attribute, value: list[TItem]):
        seen = set()
        duplicates = set()
        for item in value:
            key = selector(item)
            if key in seen:
                duplicates.add(key)
            seen.add(key)
        if len(duplicates) > 0:
            raise ValueError(f"Duplicate values found for {attribute.name}: {', '.join(map(str, duplicates))}")
    return validate

def or_(*validators: Callable[[Any, Any, Any], None]) -> Callable[[Any, Any, Any], None]:
    """Combines multiple validators with a logical OR."""
    def validate(instance, attribute, value):
        for validator in validators:
            try:
                validator(instance, attribute, value)
                return  # If any validator passes, we're done
            except Exception as e:
                logger.debug(f"Validator {validator} failed for value '{value}': {e}")
                continue  # If a validator fails, try the next one
        raise ValueError(f"Value '{value}' did not pass any of the OR validators")
    return validate

def validate_tabler_icon(instance, attribute, value):
    """Validator for Tabler icon names.
    
    Ensures that the provided icon name starts with "Tb" prefix.
    This is a simple validation to ensure consistent iconography.
    
    Args:
        instance: The instance being validated
        attribute: The attribute being validated
        value: The icon name to validate
        
    Raises:
        ValueError: If the icon name doesn't start with "Tb"
    """
    if value is None:
        return
    
    if not isinstance(value, str):
        raise ValueError(f"Icon name must be a string, got {type(value)}")
    
    # Check if icon name starts with "Tb"
    if not value.startswith("Tb"):
        raise ValueError(f"Icon name '{value}' must start with 'Tb' prefix")

def validate_compose_name_pattern(instance, attribute, value: ComposeResourceName):
    """Validator for compose resource names that must match ^[a-zA-Z0-9._-]+$.
    
    This enforces the Docker Compose specification for valid resource names,
    preventing injection attacks and ensuring compatibility across platforms.
    """
    if value is not None:
        pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        if not pattern.match(value):
            raise ValueError(f"Invalid {attribute.name} compose resource name '{value}': must match pattern ^[a-zA-Z0-9._-]+$")

# TODO: Add more validators as needed:
# - validate_challenge_difficulty (easy, medium, hard)
# - validate_points_value (positive integer, reasonable range)
# - validate_max_attempts (positive integer, reasonable limit)
# - validate_environment_variable_name (valid env var naming)
# - validate_docker_image_name (valid Docker image reference)

def validate_template_evals(instance, attribute, value):
    """Validator for Template objects to ensure they can be evaluated.
    
    This attempts to evaluate the template to catch syntax errors early
    and ensure that the template code is valid.
    
    Args:
        instance: The instance being validated
        attribute: The attribute being validated  
        value: The Template object to validate
        
    Raises:
        ValueError: If the template cannot be evaluated
    """
    if value is None:
        return  # Allow None values
    
    if not isinstance(value, Template):
        raise ValueError(f"Expected Template object, got {type(value)}")
    
    try:
        # Attempt to evaluate the template to check for syntax errors
        result = value.eval()
        logger.debug(f"Template '{value.eval_str}' for variable '{value.parent_variable}' evaluated successfully to: {result}")
    except Exception as e:
        logger.error(f"Template validation failed for variable '{value.parent_variable}' with template '{value.eval_str}': {e}")
        raise ValueError(f"Template evaluation failed for variable '{value.parent_variable}': {value.eval_str} ") from e
    
def validate_answer(instance, attribute, value: Answer):
    """Validator for answer regex patterns.
    
    Ensures that the provided answer is a valid regex pattern.
    
    Args:
        instance: The instance being validated
        attribute: The attribute being validated
        value: The answer regex to validate
        
    Raises:
        ValueError: If the answer is not a valid regex pattern
    """
    try:
        regex = re.compile(value.body)
        # If there are test cases, validate each one
        if value.test_cases:
            for test_case in value.test_cases:
                if not isinstance(test_case, AnswerTestCase):
                    raise ValueError(f"Invalid test case: {test_case}. Must be an AnswerTestCase instance.")
                if test_case.correct:
                    if not regex.fullmatch(test_case.answer):
                        raise ValueError(f"Test case answer '{test_case.answer}' does not match the regex '{value.body}'")
                else:
                    if regex.fullmatch(test_case.answer):
                        raise ValueError(f"Test case answer '{test_case.answer}' should not match the regex '{value.body}'")
    except re.error as e:
        raise ValueError(f"Invalid regex pattern for {attribute.name}: {value}") from e

def validate_regex(instance,attribute,value: str):
    """Validator for regex patterns.
    
    Ensures that the provided value is a valid regex pattern.
    
    Args:
        instance: The instance being validated
        attribute: The attribute being validated
        value: The regex pattern to validate
        
    Raises:
        ValueError: If the value is not a valid regex pattern
    """
    try:
        re.compile(value)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern for {attribute.name}: {value}") from e

def validate_cpus(instance, attribute, value: Any):
    """Validator for CPU limit values.
    
    Ensures that the provided CPU limit is a positive float or string
    that can be converted to a positive float.
    
    Args:
        instance: The instance being validated
        attribute: The attribute being validated
        value: The CPU limit to validate
    Raises:
        ValueError: If the CPU limit is larger than allowed
    """
    if value is None:
        return  # Allow None values
    
    try:
        cpu_value = float(value)
        if cpu_value <= 0:
            raise ValueError(f"CPU limit for {attribute.name} must be a positive number, got {value}")
        if cpu_value > 0.5:
            raise ValueError(f"CPU limit for {attribute.name} is too high ({value}), maximum allowed is 0.5")
    except TypeError as e:
        raise ValueError(f"CPU limit for {attribute.name} must be convertible to float, got {value}") from e