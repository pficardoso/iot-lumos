import json
import logging

from paho.mqtt import client as mqtt_client

from lumos.common.messages import (
    DetectedActionMessage,
    LedCommandMessage,
    ListenerHeartbeatMessage,
)
from lumos.led_controller.led_controller import LedController

logger = logging.getLogger("led_controller")


led_controller_obj = LedController()


def lumos_detected_action_handler(payload: str):
    logger.info("Received a detected action. Processing...")

    request_success = False

    data = DetectedActionMessage(**json.loads(payload))
    request_success = led_controller_obj.interpret_detected_action(data)

    if request_success:
        logger.info("The received detected action was processed with success")
    else:
        logger.warning("The received detected action was not processed with success")


def lumos_led_command_handler(payload: str):
    logger.info("Received a led command. Processing...")

    request_success = False

    data = LedCommandMessage(**json.loads(payload))
    request_success = led_controller_obj.interpret_led_command(data)

    if request_success:
        logger.info("The received led command was processed with success")
    else:
        logger.warning("The received led command was not processed with success")


def lumos_heartbeat_handler(payload):
    logger.info("Received a heartbeat. Processing...")

    request_success = False

    data = ListenerHeartbeatMessage(**json.loads(payload))
    led_controller_obj.interpret_heartbeat(data)

    if request_success:
        logger.info("The received heartbeat was processed with success")
    else:
        logger.warning("The received heartbeat was not processed with success")


class MQTTClient:
    DETECTED_ACTION_TOPIC = "lumos/detected_action"
    HEARTBEAT_TOPIC = "lumos/heartbeat"
    LED_COMMAND_TOPIC = "lumos/led_command"

    topic_handlers = {
        DETECTED_ACTION_TOPIC: lumos_detected_action_handler,
        HEARTBEAT_TOPIC: lumos_heartbeat_handler,
    }

    def __init__(self, client_id: str, host: str = "localhost", port: int = 1883):
        self._client_id = client_id
        self._host = host
        self._port = port
        self._client = mqtt_client.Client(client_id=client_id)
        self._client.connect(self._host, self._port)
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

    def loop_forever(self):
        logger.info(f"Starting listening for messages on {self._host}:{self._port}")
        self._client.loop_forever()

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
        else:
            logger.error("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        logger.info(f"Received message `{msg.payload}` with topic `{msg.topic}`")
        handler = self.topic_handlers.get(msg.topic)
        if handler:
            handler(msg.payload)
        else:
            # handle unknown topics
            logger.error(f"No handler for processing messages from topic {msg.topic}")


def start_led_controller_mqtt_client(broker_host: str, port: int, config_file: str):
    led_controller_obj.config(config_file)
    mqtt_client_obj = MQTTClient("lumos_led_controller", broker_host, port)
    mqtt_client_obj.loop_forever()
