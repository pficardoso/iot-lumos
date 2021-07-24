import tornado
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from src.lumos.LedController import led_controller
import logging

logger = logging.getLogger("led_controller")

class WebService():

    def __init__(self, port=8000):
        self._app = tornado.web.Application([
        ])
        self._port=port

    def start(self):
        http_server = HTTPServer(self._app)
        print(self._port)
        http_server.listen(self._port)
        print('Listening on http://localhost:%i' % self._port)
        logger.info(f"Starting web service of LedController. Listening on http://localhost:{self._port}'")
        tornado.ioloop.IOLoop.current().start()
