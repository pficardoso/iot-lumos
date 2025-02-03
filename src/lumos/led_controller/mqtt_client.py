import json
import logging

from paho.mqtt import client as mqtt_client
from paho.mqtt.matcher import MQTTMatcher

from lumos.common.messages import DetectedActionMessage, ListenerHeartbeatMessage
from lumos.integrations.rhasspy import RhasspyHelper
from lumos.led_controller.config import LedControllerConfig
from lumos.led_controller.led_controller import LedController


class MQTTClient:
    DETECTED_ACTION_TOPIC = "lumos/detected_action"
    HEARTBEAT_TOPIC = "lumos/heartbeat"
    LED_COMMAND_TOPIC = "lumos/led_command"

    def __init__(
        self,
        led_controller: LedController,
        client_id: str,
        host: str = "localhost",
        port: int = 1883,
        use_rhasspy=False,
    ):
        self._client_id = client_id
        self._host = host
        self._port = port
        self._client = mqtt_client.Client(client_id=client_id)
        self._client.connect(self._host, self._port)
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._logger = logging.getLogger("led_controller")
        self._use_rhasspy = use_rhasspy
        self.led_controller = led_controller
        self.mqtt_matcher = MQTTMatcher()
        self.topic_filters_handlers = {
            self.DETECTED_ACTION_TOPIC: self.handle_detected_action,
            self.HEARTBEAT_TOPIC: self.handle_heartbeat,
        }
        if use_rhasspy:
            self.topic_filters_handlers[
                RhasspyHelper.RHASSPY_INTENT_FILTER
            ] = self.handle_rhasspy_intent

        for topic_filter, handler in self.topic_filters_handlers.items():
            self._client.subscribe(topic_filter)
            self.mqtt_matcher[topic_filter] = handler

    def loop_forever(self):
        self._logger.info(
            f"Starting listening for messages on {self._host}:{self._port}"
        )
        self._client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._logger.info("Connected to MQTT Broker!")
        else:
            self._logger.error("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        self._logger.info(f"Received message `{msg.payload}` with topic `{msg.topic}`")

        for handler in self.mqtt_matcher.iter_match(msg.topic):
            if handler:
                handler(msg.payload)
            else:
                # handle unknown topics
                self._logger.error(
                    f"No handler for processing messages from topic {msg.topic}"
                )

    def handle_detected_action(self, payload: str):
        self._logger.info("Received a detected action. Processing...")

        request_success = False

        data = DetectedActionMessage(**json.loads(payload))
        request_success = self.led_controller.interpret_detected_action(data)

        if request_success:
            self._logger.info("The received detected action was processed with success")
        else:
            self._logger.warning(
                "The received detected action was not processed with success"
            )

    def handle_rhasspy_intent(self, payload: str):
        self._logger.info("Received an intent from rhasspy. Processing...")

        request_success = False

        data = json.loads(payload)
        try:
            led_command_msg = RhasspyHelper().convert_intent_mqtt_to_led_command_msg(
                data
            )
        except Exception:
            self._logger.exception(
                "Error while converting rhasspy intent to lumos led command"
            )
        else:
            # only executed if try finishes without errors
            request_success = self.led_controller.interpret_led_command(led_command_msg)

        if request_success:
            self._logger.info("The received intent was processed with success")
        else:
            self._logger.warning("The received intent was not processed with success")

    def handle_heartbeat(self, payload):
        self._logger.info("Received a heartbeat. Processing...")

        request_success = False

        data = ListenerHeartbeatMessage(**json.loads(payload))
        self.led_controller.interpret_heartbeat(data)

        if request_success:
            self._logger.info("The received heartbeat was processed with success")
        else:
            self._logger.warning(
                "The received heartbeat was not processed with success"
            )


def start_led_controller_mqtt_client(config: LedControllerConfig):
    led_controller = LedController()
    led_controller.config(config)
    mqtt_client_obj = MQTTClient(
        led_controller,
        "lumos_led_controller",
        config.protocol.broker_address,
        config.protocol.broker_port,
        config.use_rhasspy,
    )
    mqtt_client_obj.loop_forever()
