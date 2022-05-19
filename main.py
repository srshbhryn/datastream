import tornado.ioloop
import tornado.web
import tornado.websocket

from stream_handler import stream_managers


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
        pass


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/stream", StreamHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
