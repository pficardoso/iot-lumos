import json
import logging

import tornado
from tornado.httpserver import HTTPServer
from tornado.web import RequestHandler

from lumos.common.messages import DetectedActionMessage, ListenerHeartbeatMessage
from lumos.led_controller.led_controller import LedController

logger = logging.getLogger("led_controller")


led_controller_obj = LedController()


class ListenerRequestHandler(RequestHandler):
    def post(self):
        logger.info(
            "HttpService: received a POST request in Listener Request endpoint. Processing..."
        )

        request_success = False
        try:
            request_data = json.loads(self.request.body)
        except Exception:
            logger.error("HttpService: could not fetch data from request body")
            request_success = False

        data = DetectedActionMessage(**request_data)
        request_success = led_controller_obj.interpret_request(data)

        if request_success:
            logger.info(
                "HttpService: the POST request received in Listener Request"
                "endpoint was done successfully"
            )
            self.set_status(200)
        else:
            logger.info(
                "HttpService: the POST request received in Listener"
                "Request endpoint was done unsuccessfully"
            )
            self.set_status(400)


class ListenerHeartbeatHandler(RequestHandler):
    def post(self):
        logger.info(
            "HttpService: received a POST request in  Listener Heartbeat endpoint. Processing..."
        )

        try:
            request_data = json.loads(self.request.body)
        except Exception:
            logger.error("HttpService: could not fetch data from request body")
            self.set_status(400)

        data = ListenerHeartbeatMessage(**request_data)
        led_controller_obj.interpret_heartbeat(data)

        logger.info(
            "HttpService: the POST request received in Listener Heartbeat"
            "endpoint was done successfully"
        )
        self.set_status(200)


class HttpService:
    def __init__(self, port=8000):
        self._app = tornado.web.Application(
            [
                (r"/listener_heartbeat", ListenerHeartbeatHandler),
                (r"/listener_request", ListenerRequestHandler),
            ]
        )
        self._port = port

    def start(self):
        http_server = HTTPServer(self._app)
        print(self._port)
        http_server.listen(self._port)
        print("Listening on http://localhost:%i" % self._port)
        logger.info(
            "Starting http web service of LedController."
            f"Listening on http://localhost:{self._port}"
        )
        tornado.ioloop.IOLoop.current().start()


def start_led_controller_http_service(config_file=None):
    led_controller_obj.config(config_file)
    web_service = HttpService()
    web_service.start()
