from .redis import get_redis_client

from CTFd.utils import get_app_config

import redis_lock

def get_client_ip_round_robin():
    DOCKER_HOST = get_app_config("DOCKER_HOST").split(",")

    # Single host bypass round robin
    if len(DOCKER_HOST) == 1:
        return DOCKER_HOST[0]

    redis_client = get_redis_client(4)


    lock = redis_lock.Lock(redis_client, "ROUND_ROBIN__LOCK", expire=60)

    if lock.acquire(blocking=True):
        rr_count = redis_client.get("RR_COUNT")

        if rr_count:
            rr_count = int(rr_count)
        else:
            rr_count = 0

        rr_count = (rr_count + 1) % len(DOCKER_HOST)

        ip = DOCKER_HOST[rr_count]

        redis_client.set("RR_COUNT", str(rr_count))

        lock.release()

        return ip
