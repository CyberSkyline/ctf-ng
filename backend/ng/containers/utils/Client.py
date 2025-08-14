import docker
from .. constants import DOCKER_RUNNING

class Client(docker.DockerClient):
    def get_running(self, ctr):
        ctr = self.containers.get(ctr)
        if ctr.status != DOCKER_RUNNING:
            ctr.start()
        return ctr
