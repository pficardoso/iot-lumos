from src.lumos.ActionListener.ActionListener import ActionListener



class TimerActionListener(ActionListener):
    """"""

    def __init__(self,):
        ActionListener.__init__(self)
        self.name = "TimerActionListener"
        self.type = "TimerActionListener"
        """Constructor for TimerActionListener"""

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
        pass

    def _start_engine(self):
        pass
    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """

