
import base64
from typing import NotRequired, TypedDict
from collections.abc import Iterable

from cattrs import ClassValidationError, transform_error
from cattrs.v import format_exception
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string
from cyber_skyline.chall_parser.warnings import Warnings
import yaml

class SerializedLintMessage(TypedDict):
    field: NotRequired[str]
    message: str

class SerializedLint(TypedDict):
    warnings: NotRequired[list[SerializedLintMessage]]
    errors: NotRequired[list[SerializedLintMessage]]

def serialize_warnings(warnings: Warnings) -> list[SerializedLintMessage]:
    def serialize(parent_field: str, warning: Warnings) -> Iterable[SerializedLintMessage]:
        if warning.self_warnings:
            yield from (
                SerializedLintMessage(
                    field=f"{parent_field}.{warning.key}",
                    message=msg
                ) for msg in warning.self_warnings
            )
        for field_warning in warning.field_warnings:
            yield from serialize(f"{parent_field}.{warning.key}", field_warning)

    return list(serialize("", warnings))

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


def format_validation_error(error: Exception) -> list[SerializedLintMessage]:
    """Format validation errors in a user-friendly way using cattrs transform_error."""

    # Handle cattrs validation errors (ExceptionGroups) using transform_error
    if isinstance(error, ExceptionGroup | ClassValidationError | Exception):
        try:
            # Use cattrs' transform_error for proper ExceptionGroup handling
            error_messages = transform_error(error, format_exception=format_parse_exceptions)
            if error_messages:
                formatted_errors: list[SerializedLintMessage] = []
                for msg in error_messages:
                    # Clean up the error message formatting
                    if " @ " in msg:
                        # Split location from message for better formatting
                        parts = msg.split(" @ ", 1)
                        if len(parts) == 2:
                            formatted_errors.append(SerializedLintMessage(
                                message=parts[0],
                                field=parts[1]
                            ))
                        else:
                            formatted_errors.append(SerializedLintMessage(
                                message=msg
                            ))
                    else:
                        formatted_errors.append(SerializedLintMessage(
                            message=msg
                        ))

                return formatted_errors
        except Exception:
            # Fallback to original handling if transform_error fails
            pass

    # Fallback for ClassValidationError with __notes__ (PEP 678)
    if isinstance(error, ClassValidationError):
        errors: list[SerializedLintMessage] = []

        # Handle the main exception
        if hasattr(error, '__notes__') and error.__notes__:
            for note in error.__notes__:
                errors.append(SerializedLintMessage(
                    message=note
                ))

        # Handle nested exceptions in the group
        if hasattr(error, 'exceptions'):
            for exc in error.exceptions:
                if hasattr(exc, '__notes__') and exc.__notes__:
                    for note in exc.__notes__:
                        errors.append(SerializedLintMessage(
                            message=note
                        ))
                elif hasattr(exc, 'exceptions'):
                    # Handle nested ExceptionGroups recursively
                    for nested_exc in exc.exceptions: # type: ignore
                        if hasattr(nested_exc, '__notes__') and nested_exc.__notes__:
                            for note in nested_exc.__notes__:
                                errors.append(SerializedLintMessage(
                                    message=note
                                ))
                        else:
                            errors.append(SerializedLintMessage(
                                message=str(nested_exc)
                            ))
                else:
                    errors.append(SerializedLintMessage(
                        message=str(exc)
                    ))

        if errors:
            return errors
        else:
            return [SerializedLintMessage(
                message=f"Validation error: {str(error)}"
            )]

    # Handle other common exceptions
    elif isinstance(error, ValueError):
        return [SerializedLintMessage(
            message=f"Value error: {str(error)}"
        )]
    else:
        return [SerializedLintMessage(
            message=f"Error: {str(error)}"
        )]

def lint_challenge(yaml_content: str) -> SerializedLint | None:
    """
    Import a challenge from a YAML definition.

    :return: Any warnings or errors that were returned
    """
    try:
        compose_file = parse_compose_string(yaml_content)
        warnings = compose_file.warnings()

        if warnings.self_warnings or warnings.field_warnings:
            return {
                "warnings": serialize_warnings(warnings),
            }
        return None
    except Exception as e:
        print(e)
        return {"errors": format_validation_error(e)}