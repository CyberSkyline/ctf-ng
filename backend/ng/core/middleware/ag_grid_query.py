"""
ag-grid infinite-row-model query middleware.

Parses the block range, sort model, and filter model from the query string.
Injects them into the handler as kwargs, so endpoints don't each re-parse.
filterModel is base64-encoded JSON, matching the frontend's utf8ToBase64 scheme.
"""

import base64
import json
from functools import wraps

from flask import request

from ..exceptions import ValidationError


def ag_grid_query(f):
    """Inject start_row/end_row/sort_model/filter_model kwargs from request args."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        kwargs["start_row"] = request.args.get("startRow", 0, type=int)
        kwargs["end_row"] = request.args.get("endRow", 100, type=int)

        try:
            kwargs["sort_model"] = json.loads(request.args.get("sortModel") or "[]")
        except ValueError as e:
            raise ValidationError("Invalid sort model") from e

        raw_filter = request.args.get("filterModel")
        try:
            kwargs["filter_model"] = json.loads(base64.b64decode(raw_filter)) if raw_filter else {}
        except ValueError as e:
            raise ValidationError("Invalid filter model") from e

        return f(*args, **kwargs)

    return decorated_function
