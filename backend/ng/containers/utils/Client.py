import docker
import os 
from ..constants import DOCKER_RUNNING

class Client(docker.DockerClient):
    def get_running(self, ctr):
        ctr = self.containers.get(ctr)
        if ctr.status != DOCKER_RUNNING:
            ctr.start()
        return ctr

    def pull_image(self, image):
        auth = {
            "username": os.getenv("CONTAINER_REGISTRY_USER"),
            "password": os.getenv("CONTAINER_REGISTRY_PASSWORD"),
        }
        self.images.pull(image, auth_config=auth)

