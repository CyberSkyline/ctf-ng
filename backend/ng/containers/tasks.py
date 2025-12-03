import os
import json
import docker
import redis

from celery import Celery

redis_url = os.getenv("REDIS_URL")

app = Celery(broker=f"{redis_url}/1", result_backend=f"{redis_url}/1")

# Redis client defaults from
# ng/core/utils/redis_notifications
# Celery really doesn't like relative imports
redis_client = None

if redis_url:
    redis_client = redis.from_url(
        redis_url,
        decode_responses = True
    )
else:
    redis_client = redis.Redis(
        host = os.getenv("REDIS_HOST") or "localhost",
        port = os.getenv('REDIS_PORT') or 6379,
        db = os.getenv('REDIS_DB') or 0,
        password = os.getenv('REDIS_PASSWORD') or None,
        decode_responses = True,
        socket_connect_timeout = 5,
        socket_timeout = 5
    )

@app.task
def pull_image_celery(host, image, user_id, blueprint_id, auth_conf=None):
    tls_config = docker.tls.TLSConfig(client_cert=("/var/lib/certs/ssl/cert.pem", "/var/lib/certs/ssl/key.pem"))
    client = docker.DockerClient(base_url=f"https://{host}:2376/", tls=tls_config)
    try:
        if auth_conf:
            client.images.pull(image, auth_config=auth_conf)
        else:
            client.images.pull(image)

        # Similar to above this is what emit_notification is doing
        # these will send a notifcation when the image is done pulling
        message = {
            "user_ids": [user_id],
            "event_name": "pull-success",
            "data": { "id" : blueprint_id, "image": image }
        }

        redis_client.publish("ctf_notifications", json.dumps(message))
    except Exception as err:
        message = {
            "user_ids": [user_id],
            "event_name": "pull-fail",
            "data": { "error": str(err), "id" : blueprint_id, "image": image }
        }

        redis_client.publish("ctf_notifications", json.dumps(message))
