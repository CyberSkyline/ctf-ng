"""
Ctf-ng Update Helpers
"""

from typing import Any

def build_conditional_update_data(current_object: object, **conditional_fields: tuple[Any, bool]) -> dict[str, Any]:
    """
    Build update data with conditional logic for complex fields.
    """
    update_data: dict[str, Any] = {}
    for field_name, (new_value, condition) in conditional_fields.items():
        if condition:
            update_data[field_name] = new_value
    return update_data
