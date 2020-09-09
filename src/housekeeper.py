
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
        # self.mode = MODE.CYCLE
        # self.current_message_dict = {'foo':'bar'}
        self.notify()

    def clear_mode(self):
        if self.mode is not MODE.CLEAR:
            self.mode = MODE.CLEAR
            self.update()

    def cycle_mode(self):
        if self.mode is not MODE.CYCLE:
            self.mode = MODE.CYCLE
            self.update()

    def loading_mode(self, activity_name=None, activity_detail=None, percentage=None, activity_name_finished=None, activity_detail_finished=None):
        if self.mode is not MODE.PROGRESS:
            self.mode = MODE.PROGRESS
            self.current_message_dict = {'activity_name': activity_name,
                                         'activity_detail': activity_detail,
                                         'activity_name_finished': activity_name_finished,
                                         'activity_detail_finished': activity_detail_finished,
                                        'percentage': percentage}
            self.update()
        else:
            self.current_message_dict['activity_name'] = activity_name
            self.current_message_dict['activity_detail'] = activity_detail
            self.current_message_dict['activity_name_finished'] = activity_name_finished
            self.current_message_dict['activity_detail_finished'] = activity_detail_finished
            self.current_message_dict['percentage'] = percentage

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

