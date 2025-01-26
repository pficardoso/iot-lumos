import json
import logging

import tornado
from tornado.httpserver import HTTPServer
from tornado.web import RequestHandler

from lumos.common.messages import (
    DetectedActionMessage,
    LedCommandMessage,
    ListenerHeartbeatMessage,
)
from lumos.led_controller.led_controller import LedController


class DetectedActionRequestHandler(RequestHandler):
    def initialize(self, led_controller):
        self.logger = logging.getLogger("led_controller")
        self.led_controller = led_controller

    def post(self):
        self.logger.info(
            "HttpService: received a POST request in Listener Request endpoint. Processing..."
        )

        request_success = False
        try:
            request_data = json.loads(self.request.body)
        except Exception:
            self.logger.error("HttpService: could not fetch data from request body")
            request_success = False

        data = DetectedActionMessage(**request_data)
        request_success = self.led_controller.interpret_detected_action(data)

        if request_success:
            self.logger.info(
                "HttpService: the POST request received in Listener Request"
                "endpoint was done successfully"
            )
            self.set_status(200)
        else:
            self.logger.warning(
                "HttpService: the POST request received in Listener"
                "Request endpoint was done unsuccessfully"
            )
            self.set_status(400)


class LedCommandRequestHandler(RequestHandler):
    def initialize(self, led_controller):
        self.logger = logging.getLogger("led_controller")
        self.led_controller = led_controller

    def post(self):
        self.logger.info(
            "HttpService: received a POST request in Led Command endpoint. Processing..."
        )

        request_success = False
        try:
            request_data = json.loads(self.request.body)
        except Exception:
            self.logger.error("HttpService: could not fetch data from request body")
            request_success = False

        data = LedCommandMessage(**request_data)
        request_success = self.led_controller.interpret_led_command(data)

        if request_success:
            self.logger.info(
                "HttpService: the POST request received in Led Command"
                "endpoint was done successfully"
            )
            self.set_status(200)
        else:
            self.logger.warning(
                "HttpService: the POST request received in Led Command"
                "endpoint was done unsuccessfully"
            )
            self.set_status(400)


class ListenerHeartbeatHandler(RequestHandler):
    def initialize(self, led_controller):
        self.logger = logging.getLogger("led_controller")
        self.led_controller = led_controller

    def post(self):
        self.logger.info(
            "HttpService: received a POST request in Listener Heartbeat endpoint. Processing..."
        )

        try:
            request_data = json.loads(self.request.body)
        except Exception:
            self.logger.error("HttpService: could not fetch data from request body")
            self.set_status(400)

        data = ListenerHeartbeatMessage(**request_data)
        self.led_controller.interpret_heartbeat(data)

        self.logger.info(
            "HttpService: the POST request received in Listener Heartbeat"
            "endpoint was done successfully"
        )
        self.set_status(200)


class HttpService:
    DETECTED_ACTION_ENDPOINT = "/detected_action"
    LED_COMMAND_ENDPOINT = "/led_command"
    HEARTBEAT_ENDPOINT = "/heartbeat"

    def __init__(self, led_controller: LedController, port: int = 8000):
        self._logger = logging.getLogger("led_controller")
        self._led_controller = led_controller
        self._app = tornado.web.Application(
            [
                (
                    rf"{self.HEARTBEAT_ENDPOINT}",
                    ListenerHeartbeatHandler,
                    dict(led_controller=self._led_controller),
                ),
                (
                    rf"{self.LED_COMMAND_ENDPOINT}",
                    LedCommandRequestHandler,
                    dict(led_controller=self._led_controller),
                ),
                (
                    rf"{self.DETECTED_ACTION_ENDPOINT}",
                    DetectedActionRequestHandler,
                    dict(led_controller=self._led_controller),
                ),
            ]
        )
        self._port = port

    def start(self):
        http_server = HTTPServer(self._app)
        http_server.listen(self._port)
        print("Listening on http://localhost:%i" % self._port)
        self._logger.info(
            "Starting http web service of LedController."
            f"Listening on http://localhost:{self._port}"
        )
        tornado.ioloop.IOLoop.current().start()


def start_led_controller_http_service(port: int, config_file: str):
    led_controller = LedController()
    led_controller.config(config_file)
    web_service = HttpService(led_controller=led_controller, port=port)
    web_service.start()
