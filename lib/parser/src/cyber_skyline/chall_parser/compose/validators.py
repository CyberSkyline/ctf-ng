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
from typing import Any
from cyber_skyline.chall_parser.compose.answer import Answer, AnswerTestCase
from cyber_skyline.chall_parser.rewriter import Template
from collections.abc import Callable


logger = logging.getLogger(__name__)

def or_(*validators: Callable[[Any, Any, Any], None]) -> Callable[[Any, Any, Any], None]:
    """Combines multiple validators with a logical OR."""
    def validate(instance, attribute, value):
        for validator in validators:
            try:
                validator(instance, attribute, value)
                return  # If any validator passes, we're done
            except Exception as e:
                logger.debug(f"Validator {validator.__name__} failed for value '{value}': {e}")
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

def validate_compose_name_pattern(instance, attribute, value):
    """Validator for compose resource names that must match ^[a-zA-Z0-9._-]+$.
    
    This enforces the Docker Compose specification for valid resource names,
    preventing injection attacks and ensuring compatibility across platforms.
    """
    if value is not None:
        pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        for key in value.keys():
            if not pattern.match(key):
                raise ValueError(f"Invalid {attribute.name} key '{key}': must match pattern ^[a-zA-Z0-9._-]+$")

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