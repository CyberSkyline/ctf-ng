"""
Ctf-ng Update Helpers
"""

from typing import Any


def build_update_data(current_object: object, **field_values: Any) -> dict[str, Any]:
    """
    Build update data dictionary by comparing new values with current object.
    """
    update_data: dict[str, Any] = {}
    for field_name, new_value in field_values.items():
        if new_value is None:
            continue
        current_value = getattr(current_object, field_name, None)
        if new_value != current_value:
            update_data[field_name] = new_value
    return update_data


def build_conditional_update_data(current_object: object, **conditional_fields: tuple[Any, bool]) -> dict[str, Any]:
    """
    Build update data with conditional logic for complex fields.
    """
    update_data: dict[str, Any] = {}
    for field_name, (new_value, condition) in conditional_fields.items():
        if condition:
            update_data[field_name] = new_value
    return update_data
