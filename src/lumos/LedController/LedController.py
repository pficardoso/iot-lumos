import logging
import lumos.logger
import os
import json
import requests

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
        if self.config_data_is_valid(config_data):
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

    @staticmethod
    def config_data_is_valid(config_data: dict):

        # IMPROVEMENT: Break this function into steps. Consider to pass this logic to a new class, allowing the
        #    code reusability in other classes that require this logic during their configuration

        valid = True
        MANDATORY_FIELDS = ["name", "leds", "listeners", "listener_led_map"]

        # check if all mandatory fields exist
        missing_filds = MANDATORY_FIELDS.copy()
        for field in MANDATORY_FIELDS:
            if field in config_data.keys():
                missing_filds.remove(field)
        if len(missing_filds) != 0:
            valid = False
            raise Exception(f"Fields {missing_filds} are missing")

        # check the values in leds, listeners and listener_led_map
        # 1 - check if there are repeated devices with the same name or ip
        for x in ("leds", "listeners"):
            device_names, device_ips, repeated_names, repeated_ips = set(), set(), set(), set()
            for device_name, device_ip in config_data[x].items():

                #This next piece of code does not make sense considering that device_names are keys of a dict. During
                #the load of json data the keys are overwriten.
                #TODO: The best thing to do is to add tuples instead of tuples

                """
                if device_name in device_names:
                    repeated_names.add(device_name)
                    valid = False
                else:
                    device_names.add(device_name)
                """
                if device_ip in device_ips:
                    repeated_ips.add(device_ip)
                    valid = False
                else:
                    device_ips.add(device_ip)

            if len(repeated_names) != 0:
                raise Exception(f"Field {x} has the following names repeated: {repeated_names}")
            if len(repeated_ips) != 0:
                raise Exception(f"Field {x} has the following ips repeated: {repeated_ips}")

        # 2 - check if mapping between listener and leds are using existent leds and listeners names:
        wrong_led, wrong_listener = set(), set()
        for listener_name, led_name in config_data["listener_led_map"].items():
            if led_name not in config_data["leds"].keys():
                valid = False
                wrong_led.add(led_name)
            if listener_name not in config_data["listeners"].keys():
                valid = False
                wrong_listener.add(listener_name)

        if len(wrong_led) != 0:
            raise Exception(f"The following leds are not present in config file: ids {wrong_led}")
        if len(wrong_listener) != 0:
            raise Exception(f"The following listeners are not present in config file: ids {wrong_listener}")

        # TODO: check if there are not collisions between mapping of led and listeners.
        #   Consider if you want to avoid this and launch Exception or just to launch a warning

        return True
