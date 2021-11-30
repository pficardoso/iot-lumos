from src.lumos.ActionListener.Timer import Timer
from src.lumos.ActionListener.ActionListener import ActionListener

class ActionListerCatalog():

    def __init__(self):
        self._catalog_dict = dict()
        self._catalog_dict = {Timer.type: Timer}

    def get_action_listener(self, type:str) -> ActionListener:
        return self._catalog_dict[type]()


