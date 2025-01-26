import abc
import dataclasses
import json
import logging
import threading
import time

import requests
from pydantic import ValidationError

import lumos.logger  # noqa: F401
from lumos.action_listener.config import (
    BaseActionListenerConfig,
    HttpProtocolConfig,
    MqttProtocolConfig,
)
from lumos.common.messages import DetectedActionMessage, ListenerHeartbeatMessage


class SendMessageHelper(abc.ABC):
    @abc.abstractmethod
    def send_detected_action(self, message: DetectedActionMessage):
        """Send a detected action to the led controller"""
        raise NotImplementedError()

    @abc.abstractmethod
    def send_heartbeat(self, message: ListenerHeartbeatMessage):
        """Send a heartbeat to the led controller"""
        raise NotImplementedError()

    @abc.abstractmethod
    def check_connection_target(self) -> bool:
        """Check if the connection to the target is available"""
        raise NotImplementedError()


class HTTPSendMessageHelper(SendMessageHelper):
    def __init__(self, listener_id: str, led_controller_ip: str, port: int):
        self._listenter_id = listener_id
        self._led_controller_ip = led_controller_ip
        self._port = port
        self._logger = logging.getLogger("action_listener")

    def send_detected_action(self, message: DetectedActionMessage):
        from lumos.led_controller.http_service import HttpService

        url = (
            f"http://{self._led_controller_ip}:{self._port}"
            f"{HttpService.DETECTED_ACTION_ENDPOINT}"
        )
        requests.post(url, json=dataclasses.asdict(message), timeout=0.2)
        return

    def send_heartbeat(self, message: ListenerHeartbeatMessage):
        from lumos.led_controller.http_service import HttpService

        url = (
            f"http://{self._led_controller_ip}:{self._port}"
            f"{HttpService.HEARTBEAT_ENDPOINT}"
        )
        requests.post(url, json=dataclasses.asdict(message), timeout=0.2)
        return

    def check_connection_target(self) -> bool:
        message = ListenerHeartbeatMessage(listener_id=self._listenter_id)
        try:
            self.send_heartbeat(message)
            return True
        except requests.exceptions.ConnectionError:
            return False


class MQQTSendMessageHelper(SendMessageHelper):
    def __init__(self, listener_id: str, broker_host: str, broker_port: int):
        from paho.mqtt import client as mqtt_client

        self._broker_host = broker_host
        self._broker_port = broker_port
        self._listener_id = listener_id
        self._client = mqtt_client.Client(client_id=listener_id)
        self._client.on_connect = self.on_connect
        self._client.connect(self._broker_host, self._broker_port)
        self._logger = logging.getLogger("action_listener")

    def send_detected_action(self, message: DetectedActionMessage):
        from lumos.led_controller.mqtt_client import MQTTClient

        self._client.publish(
            MQTTClient.DETECTED_ACTION_TOPIC, json.dumps(dataclasses.asdict(message))
        )
        return

    def send_heartbeat(self, message: ListenerHeartbeatMessage):
        from lumos.led_controller.mqtt_client import MQTTClient

        self._client.publish(
            MQTTClient.HEARTBEAT_TOPIC, json.dumps(dataclasses.asdict(message))
        )
        return

    def check_connection_target(self) -> bool:
        message = ListenerHeartbeatMessage(listener_id=self._listener_id)
        try:
            self.send_heartbeat(message)
            return True
        except Exception:
            return False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._logger.info("Connected to MQTT Broker!")
        else:
            self._logger.error("Failed to connect, return code %d\n", rc)


class ActionListener(metaclass=abc.ABCMeta):
    """"""

    type = "Base"
    name = "Base"

    default_led_controller_port = 8000
    default_heartbeat_period = 660  # seconds

    def __init__(
        self,
    ):
        """Constructor for ActionListener"""
        self.id = None
        self.type = "ActionListener"
        self.configured = False
        self._heartbeat_period = None  # seconds
        self._heartbeat_thread = None
        self._send_message_helper = None
        self._logger = logging.getLogger("action_listener")

    """
    Setters/Loaders
    """

    def config(self, config_path) -> bool:
        with open(config_path) as f_conf:
            config_data = json.load(f_conf)
        self._logger.info(f"Starting configuration using {config_path} file")

        try:
            is_configured_gen = self._config_general(config_data)
            is_configured_spe = self._config_specialized(config_data)
        except ValidationError as e:
            self._logger.error(
                f"Error while configuring listener"
                f"with data {config_data} - Error: {e}"
            )
            raise

        self.configured = is_configured_gen and is_configured_spe
        return self.configured

    def _config_general(self, config_dict: dict) -> bool:
        config = BaseActionListenerConfig(**config_dict)

        self.id = config.id
        self.type = config.type
        self.protocol = config.protocol
        if isinstance(self.protocol, HttpProtocolConfig):
            self._send_message_helper = HTTPSendMessageHelper(
                self.id,
                config.protocol.led_controller_address,
                config.protocol.led_controller_port,
            )
        elif isinstance(self.protocol, MqttProtocolConfig):
            self._send_message_helper = MQQTSendMessageHelper(
                self.id, config.protocol.broker_address, config.protocol.broker_port
            )
        else:
            raise Exception(f"Protocol {self.protocol} is not supported")

        return True

    @abc.abstractmethod
    def _config_specialized(self, config_dict: dict) -> bool:
        pass

    """
    Getters
    """

    """
    Workers
    """

    @abc.abstractmethod
    def _run_engine(self):
        pass

    def _run_heartbeats_mechanism(self):
        def heartbeats_mechanism(period):
            while True:
                time.sleep(period)
                self._logger.info("Sending heartbeat")
                if self._send_message_helper.check_connection_target():
                    self._logger.info("Heartbeat sent with success")
                else:
                    self._logger.error("Heartbeat was sent unsuccessfully")

        self._heartbeat_thread = threading.Thread(
            target=heartbeats_mechanism, args=(self._heartbeat_period,), daemon=True
        )
        self._heartbeat_thread.start()

    def _send_detected_action(self, action_name, action_data=None):
        if action_data:
            if not isinstance(action_data, dict):
                raise Exception(
                    f"action_params should be a dict - {type(action_data)}  was given"
                )
        message = DetectedActionMessage(
            listener_id=self.id,
            listener_name=self.name,
            listener_type=self.type,
            action_detected=action_name,
            action_data=action_data if action_data else None,
        )
        try:
            self._send_message_helper.send_detected_action(message)
        except Exception as e:
            self._logger.error(
                f"Error while doing request to led controller with data "
                f"{dataclasses.asdict(message)} - Message error: {e}"
            )
        else:
            self._logger.info(
                f"Send with success the detected action with data {dataclasses.asdict(message)}"
            )

    def start(self):
        self._logger.info(f"Starting {self.name}...")
        if not self.configured:
            self._logger.error(f"Could not start {self.name}. Not configured")
            raise Exception("Not configured")

        if not self._send_message_helper.check_connection_target():
            msg = "Could not connect with target"
            self._logger.error(msg)
            raise Exception(msg)

        self._run_engine()  # starts the thread of engine
        self._run_heartbeats_mechanism()
        self._logger.info(f"{self.name} started")

    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """
