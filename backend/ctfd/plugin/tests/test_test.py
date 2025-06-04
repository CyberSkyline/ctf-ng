import pytest
from CTFd.models import db

from .helpers import (
    create_ctfd,
    destroy_ctfd,
)

def test():
    app = create_ctfd()
    # db.create_all()
    assert True
    destroy_ctfd(app)