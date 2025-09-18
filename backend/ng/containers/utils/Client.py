import docker
from ..constants import DOCKER_RUNNING
from ...config import CONTAINER_REGISTRY_USER, CONTAINER_REGISTRY_PASSWORD

class Client(docker.DockerClient):
    def get_running(self, ctr):
        ctr = self.containers.get(ctr)
        if ctr.status != DOCKER_RUNNING:
            ctr.start()
        return ctr

    def pull_image(self, image):
        auth = {
            "username": CONTAINER_REGISTRY_USER,
            "password": CONTAINER_REGISTRY_PASSWORD,
        }
        self.images.pull(image, auth_config=auth)

