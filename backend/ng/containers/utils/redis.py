from CTFd.utils import get_app_config
import redis

def get_redis_client(db):
    redis_client = None
    redis_url = get_app_config("REDIS_URL")

    if redis_url:
        redis_client = redis.from_url(redis_url, decode_responses=True)

    else:
        redis_client = redis.Redis(
           host=get_app_config('REDIS_HOST', 'localhost'),
           port=get_app_config('REDIS_PORT', 6379),
           db=db,
           password=get_app_config('REDIS_PASSWORD'),
           decode_responses=True,
           socket_connect_timeout=5,
           socket_timeout=5
       )
    return redis_client
