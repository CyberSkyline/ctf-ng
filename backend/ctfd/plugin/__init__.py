#!/usr/bin/env python3
from .dockerutils import get_client
import docker
from CTFd.models import db
from flask import render_template, Response

class IndividualContainer(db.Model):
    __tablename__ = 'individualcontainer'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, user):
        self.user = user
        self.client = get_client('10.100')

    def __del__(self):
        self.client.close()

    def get(self):
        return self.client.get(self.user)

    def start(self):
        try:
            container = self.get()
            if container.status != 'running':
                container.start()

        except docker.errors.NotFound:
            self.client.contianers.run('imagenamehere', detach=True, name=self.user)

    def connect_network(self, target_network):
        network = self.client.networks.get(target_network)
        network.connect(self.user, aliases=['user-host'])

    def disconnect_network(self, target_network):
        network = self.client.networks.get(target_network)
        network.disconnect(self.user)


class ChallengeContainer(db.Model):
    __tablename__ = 'challengecontainer'
    id = db.Column(db.Integer, primary_key=True)
    challenge = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    ## Image name
    image = db.Column(db.String(255))
    ## Network name
    network = db.Column(db.String(255))
    ## Alias/network name
    alias = db.Column(db.String(255))
    ## Ram override
    ramOverride = db.Column(db.Integer)

    def __init__(self, challenge):
        self.challenge = challenge



class ChallengeContianerInstance(db.Model):
    __tablename__ = 'challengecontainerinstance'
    id = db.Column(db.Integer, primary_key=True)
    ## Challenge Container
    challengeContainer = db.Column(db.Integer, db.ForeignKey('challengecontainer.id'))
    ## Team id
    team = db.Column(db.Integer, db.ForeignKey('teams.id'))

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
