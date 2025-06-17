"""
Validation functions for CTF challenge configuration.

This module provides validators for ensuring that challenge configurations
use valid values, particularly for UI elements like icons.
"""

import logging
import re


logger = logging.getLogger(__name__)

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
    
    from ..rewriter import Template
    if not isinstance(value, Template):
        raise ValueError(f"Expected Template object, got {type(value)}")
    
    try:
        # Attempt to evaluate the template to check for syntax errors
        result = value.eval()
        logger.debug(f"Template '{value.eval_str}' for variable '{value.parent_variable}' evaluated successfully to: {result}")
    except Exception as e:
        logger.error(f"Template validation failed for variable '{value.parent_variable}' with template '{value.eval_str}': {e}")
        raise ValueError(f"Template evaluation failed for variable '{value.parent_variable}': {value.eval_str} ") from e