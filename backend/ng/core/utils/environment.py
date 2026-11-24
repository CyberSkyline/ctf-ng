"""
checks the deployment the app is running in
using the .env.dev or .env.prod file
& enforces the use of the ENVIRONMENT variable
"""

import os

ENVIRONMENTS = ("development", "staging", "production")


def get_environment() -> str:
    """
    Read and validate the ENVIRONMENT variable.

    Returns:
        One of `ENVIRONMENTS`, lowercased.

    Raises:
        RuntimeError: ENVIRONMENT is unset or not a known environment
    """
    value = os.getenv("ENVIRONMENT", "").strip().lower()

    if value not in ENVIRONMENTS:
        raise RuntimeError(
            f"ENVIRONMENT must be one of {', '.join(ENVIRONMENTS)} "
            f"(got {os.getenv('ENVIRONMENT')!r}). Set it in .env.dev or .env.prod."
        )

    return value
