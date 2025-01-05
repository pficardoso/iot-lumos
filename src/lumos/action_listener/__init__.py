from lumos.action_listener.action_listener import ActionListener
from lumos.action_listener.timer import Timer


class ActionListerCatalog:
    def __init__(self):
        self._catalog_dict = dict()
        self._catalog_dict = {
            Timer.type: Timer,
        }

    def get_action_listener(self, type: str) -> ActionListener:
        return self._catalog_dict[type]()
