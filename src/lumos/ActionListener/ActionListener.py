import abc
import logging
import json
import lumos.logger
from src.lumos.ActionListener.ConfigChecker import ConfigChecker

logger = logging.getLogger("action_listener")

class ActionListener(metaclass=abc.ABCMeta):
    """"""

    default_led_controller_port = 8000

    def __init__(self,):
        """Constructor for ActionListener"""
        self.id = None
        self.type = None
        self.led_controller_ip = None
        self.led_controller_port = None
        self.configured = False
        self._config_checker = ConfigChecker()

    """
    Setters/Loaders
    """
    def config(self, config_path) -> bool:

        with open(config_path, "r") as f_conf:
            config_data = json.load(f_conf)["action_listener"]

        is_configured_gen = self._config_general(config_data)
        is_configured_spe = self._config_specialized(config_data)

        self.configured = (is_configured_gen and is_configured_spe)
        return self.configured

    def _config_general(self, config_data:dict) -> bool:

        config_check_flag = self._config_checker.check_config_data(config_data)

        self.id = config_data["id"]
        self.type = config_data["type"]
        self.led_controller_port = int(config_data["led_controller_port"]) \
                                    if "led_controller_port" in config_data.keys() \
                                    else ActionListener.default_led_controller_port
        self.led_controller_ip = config_data["led_controller_ip"]

        return config_check_flag

    @abc.abstractmethod
    def _config_specialized(self, config_path:dict) -> bool:
        pass
    """
    Getters
    """

    """
    Workers
    """

    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """

