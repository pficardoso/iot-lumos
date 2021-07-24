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
        self._listener_led_map = None
        self.host = None
        self.port = None
        self._configured = False
        self._config_checker = ConfigChecker()

    """
    Setters/Loaders
    """

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
            self._listener_led_map = config_data["listener_led_map"]
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

    """
    Workers
    """
    @led_action("toggle")
    def toggle_led(self, led_name):

        logger.info(f"Receive a request to toggle led with name {led_name}")
        if led_name not in self._leds.keys():
            logger.error(f"Led with \"{led_name}\" is not configured in LedController")

        ip = self._leds[led_name]
        logger.info(f"Sending toggle message to led \"{led_name}\", with ip {ip}")

        error_message = f"Toggle message was not sent with success to led \"{led_name}\""
        try:
            url = f"http://{ip}/win&T=2"
            response = requests.get(url)
            if response.status_code == 200:
                logger.info(f"Toggle led \"{led_name}\" done with success")
            else:
                logger.error(error_message)
        except:
            logger.error(error_message)

        return

    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """
