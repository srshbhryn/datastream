import tornado.ioloop
import tornado.web
import tornado.websocket

from stream_handler import stream_managers, get_stream_manager

class StreamHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        pass

    def on_message(self, message):
        subscription_type, stream_manager = get_stream_manager(message)
        if subscription_type == 'subscribe':
            stream_manager.add_websocket_handler(self)
        if subscription_type == 'unsubscribe':
            stream_manager.remove_websocket_handler(self)

    def on_close(self):
        for stream_manager in stream_managers.values():
            stream_manager.remove_websocket_handler(self)


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/stream", StreamHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
