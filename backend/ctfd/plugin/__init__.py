#!/usr/bin/env python3

from flask import render_template

def load(app):
    print("Plugin loaded")
  
    @app.route('/hello', defaults={'subpath':''}, methods=['GET'], strict_slashes=False)
    @app.route('/hello/<path:subpath>', methods=['GET'])
    def hello(subpath):
        return render_template('entrypoint.html')