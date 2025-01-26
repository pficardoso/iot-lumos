import json
import logging
from typing import Dict, List

import requests

import lumos.logger  # noqa: F401
from lumos.common.messages import (
    DetectedActionMessage,
    LedCommandMessage,
    ListenerHeartbeatMessage,
)
from lumos.definitions import Definitions
from lumos.led_controller.config import LedControllerConfig, ListenerLedMapConfig

definitions = Definitions()


led_action_functions = dict()


def led_action(led_action_name):
    def decorate(led_action_function):
        led_action_functions[led_action_name] = led_action_function
        return led_action_function

    return decorate


class LedController:
    """"""

    def __init__(
        self,
    ):
        """Constructor for"""
        self._logger = logging.getLogger("led_controller")
        self._logger.info("Creating object of LedController")
        self.name: str = None
        self._leds: Dict[str, str] = None  # {led_name: led_ip}
        self._listeners: Dict[str, str] = None  # {listener_name: listener_id}
        self._listeners_ids: Dict[str, str] = dict()  # {listener_id: listener_name}
        self._map_listener_led_actions: Dict[
            str, object
        ] = dict()  # {listener_name: object}
        self._configured: bool = False

    """
    Setters/Loaders
    """

    def _load_listener_led_actions_map(self, map_data: List[ListenerLedMapConfig]):
        """
        Given a list of mapping between listener and leds, it will load the given data
        into the internal mapping of the LedController. The mapping will be done as follows:
        - each listener name will be a key in the map
        - each listener_action will be a key in the listener's map
        - for each listener_action, the mapping will have a tuple of two elements
          (led_name, led_action)
        """
        for map_unit in map_data:
            listener = map_unit.listener
            listener_action = map_unit.detected_action
            led_name = map_unit.led

            if listener not in self._map_listener_led_actions:
                self._map_listener_led_actions[listener] = dict()

            listener_action, led_action = (
                map_unit.detected_action,
                map_unit.led_action,
            )
            if led_action not in led_action_functions:
                self._logger.error(
                    "During the construction of mapping between listener and leds, it was "
                    f"given an invalid led action - led action given: {led_action}"
                )
                raise Exception(
                    "Led action '{led_action}' does not exist. Please use one "
                    f"of the actions in {led_action_functions}"
                )

            self._map_listener_led_actions[listener][listener_action] = {
                "led_name": led_name,
                "led_action": led_action,
            }

    def config(self, config_path):
        self._logger.info(f"Starting configuration using {config_path} file")

        with open(config_path) as f_conf:
            config_data = json.load(f_conf)

        config_data = LedControllerConfig(**config_data)

        # makes parse of data into instance
        self.name = config_data.name
        self._leds = {
            led_name: led_config.address
            for led_name, led_config in config_data.leds.items()
        }
        self._listeners = {
            listener_name: listener_config.id
            for listener_name, listener_config in config_data.listeners.items()
        }
        for listener_name, id in self._listeners.items():
            self._listeners_ids[id] = listener_name
        self._load_listener_led_actions_map(config_data.listener_led_map)
        self._configured = True
        self._logger.info(
            f"LedController was configured successfully with name: {self.name}"
        )

    """
    Getters
    """

    def get_led_actions_list(self):
        return list(led_action_functions.keys())

    def get_listener_name_by_id(self, id):
        if id in self._listeners_ids:
            return self._listeners_ids[id]
        else:
            return None

    def get_led_and_action_through_mapping(self, listener_name, listener_action):
        success = False
        led_name, led_action = None, None
        try:
            led_name = self._map_listener_led_actions[listener_name][listener_action][
                "led_name"
            ]
            led_action = self._map_listener_led_actions[listener_name][listener_action][
                "led_action"
            ]
            success = True
        except Exception:
            pass

        return led_name, led_action, success

    """
    Workers
    """

    @led_action("toggle")
    def toggle_led(self, led_name):
        self._logger.info(f"Received a request to toggle led with name {led_name}")
        error_message = f'Toggle message was not sent with success to led "{led_name}"'

        if not self._check_led_exists(led_name):
            self._logger.error(error_message)
            return

        ip = self._leds[led_name]
        self._logger.info(f'Sending toggle message to led "{led_name}", with ip {ip}')

        try:
            url = f"http://{ip}/win&T=2"
            response = requests.get(url, timeout=0.1)
            if response.status_code == 200:
                self._logger.info(f'Toggle led "{led_name}" done with success')
            else:
                self._logger.error(error_message)
        except Exception:
            self._logger.error(error_message)

        return

    @led_action("change_rel_brightness")
    def change_led_rel_brightness(self, led_name, mode="increase"):
        error_message = (
            "Change rel brightness message was not sent with success"
            f'to led "{led_name}"'
        )
        if not self._check_led_exists(led_name):
            self._logger.error(error_message)
            return

        ip = self._leds[led_name]

        if mode == "increase":
            self._logger.info(
                f'Sending `increase brightness` message to led "{led_name}", with ip {ip}'
            )
            parameter = "~" + str(definitions.led_brigthness_step)
        elif mode == "decrease":
            self._logger.info(
                f'Sending `decrease brightness` message to led "{led_name}", with ip {ip}'
            )
            parameter = "~-" + str(definitions.led_brigthness_step)
        else:
            self._logger.error(
                f"Mode {mode} is not available in change relative brightness operation"
            )
            self._logger.error(error_message)
            return

        try:
            url = f"http://{ip}/win&A={parameter}"
            response = requests.get(url, timeout=0.2)
            if response.status_code == 200:
                self._logger.info(
                    f'Change brightness on led "{led_name}" done with success'
                )
            else:
                self._logger.error(error_message)
        except Exception:
            self._logger.error(error_message)

    def interpret_detected_action(self, data: DetectedActionMessage):
        self._logger.info(
            "Interpreting a request made by a listener: resolving listener identification..."
        )

        source_id = data.listener_id
        source_listener_name = self.get_listener_name_by_id(source_id)
        if source_listener_name is None:
            self._logger.error(
                f"Impossible to make listener identification, listener"
                f"with id '{source_id}' is not configured"
            )
            return False
        self._logger.info(
            f"Listener identification done with success. "
            f"Interpreting request made by listener '{source_listener_name}' with id '{source_id}'"
        )

        listener_action = data.action_detected
        led_name, led_action, map_success = self.get_led_and_action_through_mapping(
            source_listener_name, listener_action
        )

        if not map_success:
            self._logger.error(
                f"Could not get the target led and action related to listener "
                f"'{source_listener_name}' and action '{listener_action}'"
            )
            return False

        self._logger.info(
            "Request was interpreted with success: triggering"
            f"action '{led_action}' to led '{led_name}'"
        )
        led_action_function_to_trigger = led_action_functions[led_action]
        led_action_function_to_trigger(self, led_name)
        return True

    def interpret_led_command(self, data: LedCommandMessage):
        self._logger.info("Interpreting a led command request...")
        source_id = data.listener_id
        source_listener_name = self.get_listener_name_by_id(source_id)
        if source_listener_name is None:
            self._logger.error(
                f"Impossible to make listener identification, listener"
                f"with id '{source_id}' is not configured"
            )
            return False
        self._logger.info(
            f"Listener identification done with success. "
            f"Interpreting request made by listener '{source_listener_name}' with id '{source_id}'"
        )

        if data.command not in led_action_functions.keys():
            self._logger.error(
                f"Led command '{data.command}' is not available. "
                f"Available commands are: {led_action_functions.keys()}"
            )
            return False

        if data.target_led not in self._leds.keys():
            self._logger.error(
                f"Led '{data.target_led}' is not available. "
                f"Available leds are: {self._leds.keys()}"
            )
            return False

        self._logger.info(
            "Request was interpreted with success: triggering"
            f"action '{data.command}' to led '{data.target_led}'"
        )

        led_action_function_to_trigger = led_action_functions[data.command]
        led_action_function_to_trigger(self, data.led_name)
        return True

    def interpret_heartbeat(self, data: ListenerHeartbeatMessage):
        self._logger.info(
            "Interpreting an heartbeat received by a listener:"
            "resolving listener identification..."
        )
        source_id = data.listener_id
        source_listener_name = self.get_listener_name_by_id(source_id)
        if source_listener_name is None:
            self._logger.error(
                "Impossible to make listener identification,"
                f"listener with id '{source_id}' is not configured"
            )
            return False
        self._logger.info(
            f"Listener identification done with success. "
            f"Heartbeat received from listener '{source_listener_name}' with id '{source_id}'"
        )

        return False

    """
    Boolean methods
    """

    """
    Checkers
    """

    def _check_led_exists(self, led_name, log=True):
        exists = bool(led_name in self._leds.keys())
        if (not exists) and (log):
            self._logger.error(
                f'Led with "{led_name}" is not configured in LedController'
            )
        return exists

    """
    Util methods / Static methods
    """
