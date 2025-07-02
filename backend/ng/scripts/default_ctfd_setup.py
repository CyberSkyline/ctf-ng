#!/usr/bin/env python3

from CTFd import create_app
from tests.helpers import setup_ctfd
import os

if "SCRIPT" not in os.environ:
    raise EnvironmentError('This should only be run from a script. DO NOT run this manually.')

app = create_app()

app = setup_ctfd(
        app,
        ctf_name="CTFd",
        ctf_description="CTF description",
        name="admin",
        email="admin@examplectf.com",
        password="password",
        user_mode="users",
        ctf_theme=None,
    )
