import time

from pydantic import validator

from lumos.action_listener.action_listener import ActionListener
from lumos.action_listener.config import BaseActionListenerConfig


class TimerConfig(BaseActionListenerConfig):
    type: str = "Timer"
    timer_period: int

    @validator("type")
    def validate_type(cls, value):
        if value != "Timer":
            raise ValueError("The 'type' field must be 'Timer'.")
        return value


class Timer(ActionListener):
    """"""

    name = "Timer"
    type = "Timer"

    def __init__(
        self,
    ):
        ActionListener.__init__(self)
        self.timer_period = None
        """Constructor for Timer"""

    """
    Setters/Loaders
    """

    def _config_specialized(self, config_data: TimerConfig):
        """
        config_check_flag = self._config_checker.check_config_data(
            config_data, self.type
        )
        """
        self.timer_period = config_data.timer_period
        self._logger.info(f"Configured with time period of {self.timer_period} seconds")
        return True

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
                self._logger.info("Finished time period.")
                start_time = current_time
                self._logger.info("Starting another timer iteration")

    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """
