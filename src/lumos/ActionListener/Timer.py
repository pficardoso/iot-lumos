import threading
import time
import logging
import lumos.logger
from lumos.ActionListener.ActionListener import ActionListener

logger = logging.getLogger("action_listener")


class Timer(ActionListener):
    """"""
    name = "Timer"
    type = "Timer"

    def __init__(self,):
        ActionListener.__init__(self)
        self.timer_period = None
        """Constructor for Timer"""

    """
    Setters/Loaders
    """
    def _config_specialized(self, config_data:dict) -> bool:

        config_check_flag = self._config_checker.check_config_data(config_data, self.type)
        self.timer_period = int(config_data["timer_period"])
        logger.info(f"Configured with time period of {self.timer_period} seconds")

        return config_check_flag

    """
    Getters
    """

    """
    Workers
    """

    def _run_engine(self):
        start_time = time.time()
        while True:
            current_time = time.time()
            if (current_time - start_time) > self.timer_period:
                self._send_detected_action("timeout")
                logger.info("Finished time period.")
                start_time = current_time
                logger.info("Starting another timer iteration")

    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """

