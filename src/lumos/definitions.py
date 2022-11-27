import os


class SingletonMeta(type):
    """
     https://refactoring.guru/design-patterns/singleton/python/example
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Definitions(metaclass=SingletonMeta):

    def __init__(self):
        self.root_dir   = "/".join(__file__.split("/")[0:-3])
        self.conf_dir   = os.path.join(self.root_dir, "configs")
        self.log_dir    = os.path.join(self.root_dir, "logs")
        self.models_dir = os.path.join(self.root_dir, "models")

        self.led_brigthness_step = int(255/10)