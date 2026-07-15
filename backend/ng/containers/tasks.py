import os
import json
import time
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
        pull_kwargs = {"stream": True, "decode": True}
        if auth_conf:
            pull_kwargs["auth_config"] = auth_conf

        # keep track of layer sizes and progress for weighted average
        layers = {}

        # send initial 0 progress notification so the client knows the pull has started
        # otherwise, there may be a bit of a delay while docker thinks
        message = {
            "user_ids": [user_id],
            "event_name": "pull-progress",
            "data": { "id": blueprint_id, "image": image, "percent": 0 }
        }

        redis_client.publish("ctf_notifications", json.dumps(message))
        last_emit = time.monotonic()

        # pull the image and loop over the generator of per-layer progress events
        for event in client.api.pull(image, **pull_kwargs):
            # runs for each layer status update
            layer_id = event.get("id")
            detail = event.get("progressDetail")
            status = event.get("status")

            if layer_id and detail and detail.get("total"):
                # store layer progress as we receive status updates.
                # total is doubled to account for both download and extract phases, since both must finish for the layer to be at 100%.
                if status == "Downloading":
                    # download phase, (current/total) runs 0 -> 0.5
                    layers[layer_id] = { "total": detail["total"] * 2, "current": detail["current"] }
                elif status == "Extracting" and layer_id in layers:
                    # extract phase, (current/total) runs 0.5 -> 1
                    layers[layer_id]["progress"] = detail["total"] + detail["current"]

            # throttle socket notifications since the generator is noisy
            now = time.monotonic()
            if layers and now - last_emit > 1:
                current_sum = sum(layer["current"] for layer in layers.values())
                total_sum = sum(layer["total"] for layer in layers.values())
                percent = round(current_sum / total_sum * 100, 1)

                message = {
                    "user_ids": [user_id],
                    "event_name": "pull-progress",
                    "data": { "id": blueprint_id, "image": image, "percent": percent }
                }

                redis_client.publish("ctf_notifications", json.dumps(message))
                last_emit = now

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
