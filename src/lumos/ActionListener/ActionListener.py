import abc
import logging
import lumos.logger

logger = logging.getLogger("action_listener")

class ActionListener(metaclass=abc.ABCMeta):
    """"""

    def __init__(self,):
        """Constructor for ActionListener"""
        self.id = None
        self.type = None
        self.led_controller_ip = None
        self.led_controller_port = None
        self.configured = False

    """
    Setters/Loaders
    """
    def config(self, config_path) -> bool:
        is_configured_gen = self._config_general(config_path)
        is_configured_spe = self._config_specialized(config_path)
        self.configured = (is_configured_gen and is_configured_spe)
        return

    def _config_general(self, config_path) -> bool:
        #TODO
        pass

    @abc.abstractmethod
    def _config_specialized(self, config_path):
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

