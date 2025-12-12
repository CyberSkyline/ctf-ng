from flask import request, session
from flask_limiter import Limiter


def session_key():
    return session.get("id") or request.remote_addr

limiter = Limiter(
    session_key,
    strategy="moving-window",
)
