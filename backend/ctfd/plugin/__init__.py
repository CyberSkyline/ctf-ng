#!/usr/bin/env python3
from .dockerutils import get_client
## from .models import IndividualContainer
from flask import render_template, Response

def load(app):
    app.db.create_all()

    @app.route('/hello', defaults={'subpath':''}, methods=['GET'], strict_slashes=False)
    @app.route('/hello/<path:subpath>', methods=['GET'])
    def hello(subpath):
        return render_template('entrypoint.html')

    @app.route('/containers', methods=['GET'])
    def ctrs():
        client = get_client('10.100.20.246')
        ctrs = client.containers.list()
        headers = { 'Content-Type': 'text/plain' }
        return Response(f'Containers {len(ctrs)}', status=200, headers=headers)
    print("Plugin loaded")
