"""
File handling utility functions
"""

import filetype
from werkzeug.datastructures import FileStorage


def get_file_size(file: FileStorage) -> int:
    """
    Get the size of a FileStorage object without loading it into memory

    Args:
        file: FileStorage object from Flask request

    Returns:
        int: File size in bytes
    """
    current_pos = file.tell()

    file.seek(0, 2)
    file_size = file.tell()

    file.seek(current_pos)

    return file_size

def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.

    Args:
        filename: Name of the file

    Returns:
        str: File extension without the dot, lowercase
        Empty string if no extension.
    """
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[-1].lower()


def validate_image_content(file: FileStorage) -> tuple[str, str]:
    """
    Validate that the file is actually an image and get its true type

    Args:
        file: FileStorage object from Flask request

    Returns:
        Tuple[str, str]: (image_format, content_type)
            - image_format: 'webp', 'png', 'jpg', etc.
            - content_type: 'image/webp', 'image/png', etc.

    Raises:
        ValueError: If the file is not a valid image
    """
    kind = filetype.guess(file)
    file.seek(0)

    if kind is None or not kind.mime.startswith('image/'):
        raise ValueError("File is not a valid image")

    image_format = kind.extension
    content_type = kind.mime

    return image_format, content_type
