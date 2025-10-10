import base64

import boto3
import docker
from CTFd.utils import get_app_config

from ..constants import DOCKER_RUNNING


class Client(docker.DockerClient):
    def get_running(self, ctr):
        ctr = self.containers.get(ctr)
        if ctr.status != DOCKER_RUNNING:
            ctr.start()
        return ctr

    def get_network_by_name(self, network_name: str):
        return self.networks.list(names=[f"^{network_name}$"])[0]

    def get_ecr_credentials(self):
        """Get AWS ECR login credentials using boto3"""
        # Get AWS credentials from app config
        aws_access_key = get_app_config("CONTAINER_REGISTRY_USER")
        aws_secret_key = get_app_config("CONTAINER_REGISTRY_PASSWORD")
        region = get_app_config("AWS_REGION", "us-east-1")  # Default to us-east-1 if not set

        # Create a boto3 ECR client with the credentials
        ecr_client = boto3.client(
            "ecr", region_name=region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key
        )

        # Get authorization token (valid for 12 hours)
        response = ecr_client.get_authorization_token()

        # The response includes authorization data
        auth_data = response["authorizationData"][0]

        # The token comes base64-encoded
        token = base64.b64decode(auth_data["authorizationToken"]).decode("utf-8")
        username, password = token.split(":")

        # Return the Docker-compatible auth dict
        return {
            "username": username,  # Typically "AWS"
            "password": password,  # The actual token
            "registry": auth_data["proxyEndpoint"],
        }

    def pull_image(self, image):
        try:
            # First try to get ECR credentials
            auth = self.get_ecr_credentials()
            print("Using ECR authentication")
        except Exception:
            # Fall back to regular registry auth if ECR auth fails
            print("Using standard registry authentication")
            auth = {
                "username": get_app_config("CONTAINER_REGISTRY_USER"),
                "password": get_app_config("CONTAINER_REGISTRY_PASSWORD"),
            }

        self.images.pull(image, auth_config=auth)
