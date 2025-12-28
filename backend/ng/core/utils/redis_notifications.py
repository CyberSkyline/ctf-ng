"""
Redis pub/sub system for inter-server notification communication
"""

import json
import threading
import time
import redis
from flask import current_app
from .logger import get_logger


logger = get_logger(__name__)


NOTIFICATION_CHANNEL = "ctf_notifications"


class RedisNotificationManager:
    """
    Manages Redis pub/sub for notifications across multiple server instances
    """
    def __init__(self, socketio = None):
        self.socketio = socketio
        self.redis_client = None
        self.pubsub = None
        self.subscriber_thread = None
        self.should_stop = False
        self._initialize_redis()

    def _initialize_redis(self):
        """
        Initialize Redis connection
        """
        try:
            redis_url = current_app.config.get('REDIS_URL')
            if redis_url:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses = True
                )
            else:
                self.redis_client = redis.Redis(
                    host = current_app.config.get('REDIS_HOST',
                                                  'localhost'),
                    port = current_app.config.get('REDIS_PORT',
                                                  6379),
                    db = current_app.config.get('REDIS_DB',
                                                0),
                    password = current_app.config.get('REDIS_PASSWORD'),
                    decode_responses = True,
                    socket_connect_timeout = 5,
                    socket_timeout = 5
                )

            self.redis_client.ping()
            logger.info("Redis connection established for notifications")

        except Exception as e:
            logger.error("Failed to initialize Redis for notifications: %s", e)
            self.redis_client = None

    def publish_notification(self, user_ids, event_name, data):
        """
        Publish notification event to Redis for all server instances

        Args:
            user_ids: List of user IDs who should receive the notification
            event_name: Name of the socket event
            data: Event data
        """
        if not self.redis_client:
            logger.warning("Redis not available, cannot publish notification")
            return

        try:
            message = {
                "user_ids": user_ids if isinstance(user_ids,
                                                   list) else [user_ids],
                "event_name": event_name,
                "data": data
            }

            self.redis_client.publish(
                NOTIFICATION_CHANNEL,
                json.dumps(message)
            )
            logger.debug(
                "Published notification to Redis: %s for %d users",
                event_name, len(message['user_ids'])
            )

        except Exception as e:
            logger.error("Failed to publish notification to Redis: %s", e)

    def start_subscriber(self):
        """
        Start Redis subscriber in a background thread with reconnection logic
        """
        if not self.redis_client or not self.socketio:
            logger.warning(
                "Cannot start Redis subscriber - Redis or SocketIO not available"
            )
            return

        self.socketio.start_background_task(self._subscriber_worker)
        logger.info("Redis notification subscriber started")

    def _subscriber_worker(self):
        """
        Background worker that listens for Redis messages and sends to connected clients
        """
        logger.info("Redis subscriber worker started")

        while not self.should_stop:
            try:
                pubsub = self.redis_client.pubsub()
                pubsub.subscribe(NOTIFICATION_CHANNEL)

                for message in pubsub.listen():
                    if self.should_stop:
                        break

                    if message['type'] == 'message':
                        try:
                            data = json.loads(message['data'])
                            self._handle_notification_message(data)
                        except Exception as e:
                            logger.error(
                                "Error processing Redis message: %s", e
                            )

            except Exception as e:
                logger.error("Redis subscriber error: %s", e)
                time.sleep(5)

        logger.info("Redis subscriber worker stopped")

    def _handle_notification_message(self, message):
        """
        Handle incoming notification message from Redis

        Args:
            message: Parsed message dict with user_ids, event_name, data
        """
        user_ids = message.get('user_ids', [])
        event_name = message.get('event_name')
        data = message.get('data')

        if not user_ids or not event_name:
            logger.warning("Invalid notification message: %s", message)
            return
        from ...notifications.sockets import get_user_connections

        for user_id in user_ids:
            user_sids = get_user_connections(user_id)
            for sid in user_sids:
                try:
                    self.socketio.emit(event_name, data, to = sid)
                except Exception as e:
                    logger.error(
                        "Failed to send notification to SID %s: %s", sid, e
                    )

        logger.debug(
            "Delivered %s to %d connections",
            event_name, len([sid for user_id in user_ids for sid in get_user_connections(user_id)])
        )

    def stop_subscriber(self):
        """
        Stop the Redis subscriber gracefully
        """
        self.should_stop = True

        if self.pubsub:
            try:
                self.pubsub.close()
            except Exception:
                pass

        if self.subscriber_thread and self.subscriber_thread.is_alive():
            self.subscriber_thread.join(timeout = 10)

        logger.info("Redis notification subscriber stopped")


# Global instance
redis_notification_manager = None


def initialize_redis_notifications(socketio):
    """
    Initialize the global Redis notification manager
    """
    global redis_notification_manager
    redis_notification_manager = RedisNotificationManager(socketio)
    redis_notification_manager.start_subscriber()
    return redis_notification_manager


def get_redis_notification_manager():
    """
    Get the global Redis notification manager instance
    """
    return redis_notification_manager
