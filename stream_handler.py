import asyncio
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
import redis.asyncio as redis

from config import REDIS_HOST, REDIS_PORT, REDIS_DB, STREAM_KEYS


class StreamManager:
    def __init__(self, stream_key):
        self.stream_key = stream_key
        self.websocket_handlers = set()

    def add_websocket_handler(self, wsh):
        self.websocket_handlers.add(wsh)

    def remove_websocket_handler(self, wsh):
        self.websocket_handlers.remove(wsh)

    def message_handler(self, message):
        for wsh in self.websocket_handlers:
            tornado.ioloop.IOLoop.current().add_callback(wsh.write_message, message)


def get_stream_manager(subscription_message):
    if ':' not in subscription_message:
        return None, None
    subscription_data = subscription_message.split(':')
    if not len(subscription_data) == 2:
        return None, None
    subscription_type, subscription_key = subscription_data
    if not (
        subscription_type in ['subscribe', 'unsubscribe',]
        and
        subscription_key in stream_managers
    ):
        return None, None
    return subscription_type, stream_managers[subscription_key]


stream_managers = {
    stream_key: StreamManager(stream_key)
    for stream_key in STREAM_KEYS
}

class Redis:
    def __init__(self) -> None:
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.db = REDIS_DB
        self.stream_keys = STREAM_KEYS
        self.ioloop = tornado.ioloop.IOLoop.current()

    async def start(self):
        try:
            self.client = redis.Redis(host=self.host, port=self.port, db=self.db)
        except Exception as e:
            asyncio.sleep(1)
            self.ioloop.add_callback(self.start)
            return
        self.ioloop.add_callback(self.watch_streams)

    async def watch_streams(self):
        try:
            response = await self.client.brpop(self.stream_keys)
            stream_key, stream_data = response
            stream_key = stream_key.decode('utf-8')
            stream_managers[stream_key].message_handler(stream_data)
            self.ioloop.add_callback(self.watch_streams)
        except Exception as e:
            self.ioloop.add_callback(self.start)
