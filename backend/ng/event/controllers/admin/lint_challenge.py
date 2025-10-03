
import base64
from typing import NotRequired, TypedDict

from cattrs import ClassValidationError, transform_error
from cattrs.v import format_exception
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string
from cyber_skyline.chall_parser.warnings import Warnings
import yaml

class SerializedWarnings(TypedDict):
    field: str
    warnings: list[str | 'SerializedWarnings']

class SerializedLint(TypedDict):
    warnings: NotRequired[SerializedWarnings]
    errors: NotRequired[list[str]]

def serialize_warnings(warnings: Warnings) -> SerializedWarnings:
    return {
        "field": warnings.key,
        "warnings": warnings.self_warnings + [serialize_warnings(w) for w in warnings.field_warnings],
    }

def format_parse_exceptions(error: BaseException, type: type | None) -> str:
    """Format parse exceptions for better readability."""
    if isinstance(error, KeyError):
        return f"Required field {str(error)} missing"
    elif isinstance(error, ValueError):
        return f"Value error: {str(error)}"
    elif isinstance(error, FileNotFoundError):
        return f"File not found: {str(error)}"
    elif isinstance(error, yaml.YAMLError):
        return f"YAML error: {str(error)}"
    return format_exception(error, type)


def format_validation_error(error: Exception) -> list[str]:
    """Format validation errors in a user-friendly way using cattrs transform_error."""

    # Handle cattrs validation errors (ExceptionGroups) using transform_error
    if isinstance(error, ExceptionGroup | ClassValidationError | Exception):
        try:
            # Use cattrs' transform_error for proper ExceptionGroup handling
            error_messages = transform_error(error, format_exception=format_parse_exceptions)
            if error_messages:
                formatted_errors = []
                for msg in error_messages:
                    # Clean up the error message formatting
                    if " @ " in msg:
                        # Split location from message for better formatting
                        parts = msg.split(" @ ", 1)
                        if len(parts) == 2:
                            formatted_errors.append(f"{parts[0]} (at {parts[1]})")
                        else:
                            formatted_errors.append(msg)
                    else:
                        formatted_errors.append(msg)

                return formatted_errors
        except Exception:
            # Fallback to original handling if transform_error fails
            pass

    # Fallback for ClassValidationError with __notes__ (PEP 678)
    if isinstance(error, ClassValidationError):
        errors = []

        # Handle the main exception
        if hasattr(error, '__notes__') and error.__notes__:
            for note in error.__notes__:
                errors.append(note)

        # Handle nested exceptions in the group
        if hasattr(error, 'exceptions'):
            for exc in error.exceptions:
                if hasattr(exc, '__notes__') and exc.__notes__:
                    for note in exc.__notes__:
                        errors.append(note)
                elif hasattr(exc, 'exceptions'):
                    # Handle nested ExceptionGroups recursively
                    for nested_exc in exc.exceptions: # type: ignore
                        if hasattr(nested_exc, '__notes__') and nested_exc.__notes__:
                            for note in nested_exc.__notes__:
                                errors.append(note)
                        else:
                            errors.append(str(nested_exc))
                else:
                    errors.append(str(exc))

        if errors:
            return errors
        else:
            return [f"Validation error: {str(error)}"]

    # Handle other common exceptions
    elif isinstance(error, ValueError):
        return [f"Value error: {str(error)}"]
    else:
        return [f"Error: {str(error)}"]

def import_challenge_from_yaml(json_data) -> SerializedLint | None:
    """
    Import a challenge from a YAML definition.

    :return: Any warnings or errors that were returned
    """
    payload = base64.urlsafe_b64decode(json_data["yaml"])

    try:
        compose_file = parse_compose_string(payload.decode("utf-8"))
        warnings = compose_file.warnings()

        if warnings.self_warnings or warnings.field_warnings:
            return {
                "warnings": serialize_warnings(warnings),
            }
        return None
    except Exception as e:
        print(e)
        return {"errors": format_validation_error(e)}