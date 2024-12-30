from lumos.ActionListener.Timer import Timer
from lumos.ActionListener.HandClapDetector import HandClapDetector
from lumos.ActionListener.ActionListener import ActionListener

class ActionListerCatalog():

    def __init__(self):
        self._catalog_dict = dict()
        self._catalog_dict = {Timer.type: Timer,
                              HandClapDetector.type: HandClapDetector}

    def get_action_listener(self, type:str) -> ActionListener:
        return self._catalog_dict[type]()


