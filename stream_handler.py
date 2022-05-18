import tornado.ioloop
import tornado.web
import tornado.websocket
import redis
import tornado.gen

# classtornado.tcpclient.TCPClient



redis_client = redis.Redis(host='localhost', port=6379, db=0)



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

    # @tornado.gen.coroutine
    async def watch(self):
        print('aaa', self.stream_key)
        response = yield redis_client.brpop(self.stream_key)
        print('bbb', self.stream_key)
        self.message_handler(response[1])
        tornado.ioloop.IOLoop.current().add_callback(self.watch)


stream_keys = [
    'test1',
    'test2',
]

stream_managers = {
    stream_key: StreamManager(stream_key)
    for stream_key in stream_keys
}
