"""
List available certificate templates
"""

import os

from ...config import CERTIFICATES_DIR


def list_certificate_templates() -> list[str]:
    """
    List available certificate templates.

    Returns:
        list[str]: Relative paths of available .typ template files
    """
    templates = []
    for root, _dirs, files in os.walk(CERTIFICATES_DIR):
        for filename in files:
            if filename.endswith(".typ") and not filename.startswith("_"):
                relative_path = os.path.relpath(os.path.join(root, filename), CERTIFICATES_DIR)
                templates.append(relative_path.replace(os.sep, "/"))

    return sorted(templates)
