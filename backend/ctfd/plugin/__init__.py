#!/usr/bin/env python3

from flask import render_template

from CTFd.utils.challenges import get_all_challenges

def print_challenges():
    challenges = get_all_challenges()

    print(challenges, flush=True)

def load(app):
    print_challenges()

    @app.route('/hello', defaults={'subpath':''}, methods=['GET'], strict_slashes=False)
    @app.route('/hello/<path:subpath>', methods=['GET'])
    def hello(subpath):
        print_challenges()

        return render_template('entrypoint.html')