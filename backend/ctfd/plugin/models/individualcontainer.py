import docker
from CTFd.models import db

# This will probably end up being apart of
# The ORM object
class IndividualContainer(db.Model):
    __tablename__ = 'individualcontainer'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, user):
        self.user = user
        self.client = docker.from_env()

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
