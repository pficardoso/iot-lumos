import threading
import time
import logging
import lumos.logger
from src.lumos.ActionListener.ActionListener import ActionListener

logger = logging.getLogger("action_listener")


class Timer(ActionListener):
    """"""
    name = "Timer"
    type = "Timer"

    def __init__(self,):
        ActionListener.__init__(self)
        """Constructor for Timer"""

    """
    Setters/Loaders
    """
    def _config_specialized(self, config_data:dict) -> bool:

        config_check_flag = self._config_checker.check_config_data(config_data, self.type)
        self.timer_period = int(config_data["timer_period"])

        return config_check_flag

    """
    Getters
    """

    """
    Workers
    """
    def _build_engine(self):
        logger.info("Building engine")

        def timer_mechanism():
            start_time = time.time()
            while True:
                current_time = time.time()
                if (current_time - start_time) > self.timer_period:
                    self._add_detected_action("timeout")
                    logger.info("Finished time period.")
                    start_time = current_time
                    logger.info("Starting another timer iteration")

        self._timer_thread = threading.Thread(target=timer_mechanism)

    def _start_engine(self):
        self._timer_thread.start()
    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """

