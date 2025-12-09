from functools import wraps
from flask import request
from ..utils import error_response


def max_content_length(limit: int):
  def decorator(f):
      @wraps(f)
      def decorated_function(*args, **kwargs):
          if request.content_length is not None and request.content_length > limit:
              return error_response(
                  "Request body exceeds maximum allowed size",
                  "content_size",
                  413,
              )
          else:
              return f(*args, **kwargs)

      return decorated_function

  return decorator
