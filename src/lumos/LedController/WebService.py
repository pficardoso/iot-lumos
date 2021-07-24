import tornado
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import RequestHandler
from src.lumos.LedController import led_controller
import logging
import json

logger = logging.getLogger("led_controller")


class ListenerRequestHandler(RequestHandler):

    def post(self):
        logger.info("WebService: received a POST request in Listener Request endpoint. Processing...")

        request_success = False
        try:
            request_data = json.loads(self.request.body)
        except:
            logger.error("WebService: could not fetch data from request body")
            request_success = False

        request_success = led_controller.interpret_request(request_data)

        if request_success:
            logger.info("WebService: the POST request received in Listener Request endpoint was done successfully")
        else:
            logger.info("WebService: the POST request received in Listener Request endpoint was done unsuccessfully")

class WebService():

    def __init__(self, port=8000):
        self._app = tornado.web.Application([
            (r"/listener_request", ListenerRequestHandler)
        ])
        self._port=port

    def start(self):
        http_server = HTTPServer(self._app)
        print(self._port)
        http_server.listen(self._port)
        print('Listening on http://localhost:%i' % self._port)
        logger.info(f"Starting web service of LedController. Listening on http://localhost:{self._port}'")
        tornado.ioloop.IOLoop.current().start()
