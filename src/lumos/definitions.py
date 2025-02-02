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
        self.root_dir = "/".join(__file__.split("/")[0:-3])
        self.conf_dir = os.path.join(self.root_dir, "configs")
        self.log_dir = os.path.join(self.root_dir, "logs")
        self.models_dir = os.path.join(self.root_dir, "models")

        self.led_brigthness_step = int(255 / 10)
        self.colors_rgb_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 192, 203),
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "gray": (128, 128, 128),
            "brown": (165, 42, 42),
            "turquoise": (64, 224, 208),
            "silver": (192, 192, 192),
            "gold": (218, 165, 32),
        }
