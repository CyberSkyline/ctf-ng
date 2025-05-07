#!/usr/bin/env python3

from flask import render_template

def load(app):
  print("Plugin loaded")
  
  @app.route('/hello', methods=['GET'])
  def hello():
    return render_template('entrypoint.html')
