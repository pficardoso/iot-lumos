import logging
import lumos.logger
import os
import json
import requests
from src.lumos.LedController.ConfigChecker import ConfigChecker

logger = logging.getLogger("led_controller")

led_action_functions = dict()

def led_action(led_action_name):
    def decorate(led_action_function):
        led_action_functions[led_action_name] = led_action_function
        return led_action_function
    return decorate


class LedController:
    """"""

    def __init__(self, ):
        """Constructor for """
        logger.info(f"Creating object of LedController")
        self.name = None
        self._leds = None
        self._listeners = None
        self._listeners_ids = dict()
        self._map_listener_led_actions = dict()
        self.host = None
        self.port = None
        self._configured = False
        self._config_checker = ConfigChecker()

    """
    Setters/Loaders
    """
    def _load_listener_led_actions_map(self, map_data:list):
        for map_unit in map_data:
            listener = map_unit["listener"]
            listener_action = map_unit["listener_action"]
            led_name = map_unit["led"]

            if listener not in self._map_listener_led_actions:
                self._map_listener_led_actions[listener] = dict()


            listener_action, led_action = map_unit["listener_action"], map_unit["led_action"]
            if led_action not in led_action_functions:
                logger.error(f"During the construction of mapping between listener and leds, it was given an invalid"
                             "led action - led action given: {led_action}")
                raise Exception(f"Led action '{led_action}' does not exist. Please use one "
                                f"of the actions in {led_action_functions}")

            self._map_listener_led_actions[listener][listener_action] = {"led_name":led_name, "led_action":led_action}


    def config(self, config_path):

        logger.info(f"Starting configuration using {config_path} file")

        if not os.path.isfile(config_path):
            raise Exception(f"{config_path} file does not exist")
        if config_path.split(".")[-1] != "json":
            raise Exception(f"{config_path} does not have .json extension")

        with open(config_path, "r") as f_conf:
            config_data = json.load(f_conf)["led_controller"]

        # check validity of config data
        if self._config_checker.check_config_data(config_data):
            # makes parse of data into instance
            self.name = config_data["name"]
            self._leds = config_data["leds"]
            self._listeners = config_data["listeners"]
            for listener_name, listener_data in self._listeners.items():
                self._listeners_ids[listener_data["id"]] = listener_name
            self._load_listener_led_actions_map(config_data["listener_led_map"])
            self._configured = True
            logger.info(f"LedController was configured successfully with name: {self.name}")
        else:
            logger.error(f"Data from config file is not valid.")
            raise Exception(f"Data from {config_path} is not valid")


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
            led_name = self._map_listener_led_actions[listener_name][listener_action]["led_name"]
            led_action = self._map_listener_led_actions[listener_name][listener_action]["led_action"]
            success = True
        except:
            pass

        return led_name, led_action, success


    """
    Workers
    """
    @led_action("toggle")
    def toggle_led(self, led_name):

        logger.info(f"Received a request to toggle led with name {led_name}")
        if led_name not in self._leds.keys():
            logger.error(f"Led with \"{led_name}\" is not configured in LedController")

        ip = self._leds[led_name]
        logger.info(f"Sending toggle message to led \"{led_name}\", with ip {ip}")

        error_message = f"Toggle message was not sent with success to led \"{led_name}\""
        try:
            url = f"http://{ip}/win&T=2"
            response = requests.get(url, timeout=0.1)
            if response.status_code == 200:
                logger.info(f"Toggle led \"{led_name}\" done with success")
            else:
                logger.error(error_message)
        except:
            logger.error(error_message)

        return

    def interpret_request(self, request_data: dict):

        logger.info("Interpreting a request made by a listener: resolving listener identification...")

        if "id" not in request_data:
            logger.error("Impossible to make listener identification, id was not given")
            return False
        source_id = request_data["id"]

        source_listener_name = self.get_listener_name_by_id(source_id)
        if source_listener_name == None:
            logger.error(f"Impossible to make listener identification, listener with id '{source_id}' is not configured")
            return False
        logger.info(f"Listener identification done with success. "
                    f"Interpreting request made by listener '{source_listener_name}' with id '{source_id}'")

        if "listener_action" not in request_data:
            logger.error(f"Impossible to interpret_request, listener_action was not given in request")
            return False

        listener_action = request_data["listener_action"]
        led_name, led_action, map_success = self.get_led_and_action_through_mapping(source_listener_name, listener_action)

        if not map_success:
            logger.error(f"Could not get the target led and action related to listener "
                         f"'{source_listener_name}' and action '{listener_action}'")
            return False

        logger.info(f"Request was interpreted with success: triggering action '{led_action}' to led '{led_name}'")
        led_action_function_to_trigger = led_action_functions[led_action]
        led_action_function_to_trigger(self, led_name)
        return True

    def interpret_heartbeat(self, request_data:dict):
        logger.info("Interpreting an heartbeat received by a listener: resolving listener identification...")

        if "id" not in request_data:
            logger.error("Impossible to make listener identification, id was not given")
            return False
        source_id = request_data["id"]

        source_listener_name = self.get_listener_name_by_id(source_id)
        if source_listener_name == None:
            logger.error(f"Impossible to make listener identification, listener with id '{source_id}' is not configured")
            return False
        logger.info(f"Listener identification done with success. "
                    f"Heartbeat received from listener '{source_listener_name}' with id '{source_id}'")

        return False


    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """

