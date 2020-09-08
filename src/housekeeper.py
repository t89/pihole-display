
from observer import Observer, Subject
from led_display import MODE
from typing import List

class Housekeeper(Subject):

    # _mode: int = 0
    # _current_message_dict: dict = None

    _observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    ##
    # Observer management
    def notify(self) -> None:
        """ Trigger an update in each observer """
        for observer in self._observers:
            observer.update(self)

    def __init__(self):
        ##
        # Initial Mode
        self.mode = MODE.CLEAR
        self.current_message_dict = {}
        super(Housekeeper, self).__init__()

    ##
    # Pihole Management
    def update(self):
        self.mode = MODE.PROGRESS
        self.current_message_dict = {'foo':'bar'}
        self.notify()

    ##
    # Setter & Getter
    # def get_mode(self):
    #     return _mode

    # def set_mode(self, mode: MODE):
    #     _mode = mode

    # def get_current_message_dict(self):
    #     return _current_message_dict

    # def set_current_message_dict(self, cmd: dict):
    #     _current_message_dict = cmd

