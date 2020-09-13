
import subprocess
from observer import Observer, Subject
from led_display import MODE
from typing import List
from network import NetworkManager
from enum import Enum
from time import sleep

class PIHOLE_MODULE(Enum):
    CORE = 0
    FTL = 1
    WEB = 2

class MESSAGE_TYPE(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2

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
        self.encoding = 'utf-8'
        self.mode = MODE.CLEAR
        self.current_message_dict = {}
        self.network_manager = NetworkManager.get_instance()
        super(Housekeeper, self).__init__()

    def cmd(self, cmd):
        """ Run command in shell and return result """
        return subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT).stdout.read().decode(self.encoding)

    def reboot(self):
        """ Reboots the machine """
        self.reboot_mode()
        sleep(1)
        self.cmd('sudo reboot')

    def connection_check_with_wps(self):
        """ Checks if no internet and no wifi connections exist. If non are available,
        attempts WPS every 15 seconds for 15 times before rebooting. Will copy the backup
        configuration after 10 attempts  """

        counter = 1

        WPS_MESSAGES_STATE_1 = ['Press WPS button', 'on your router']
        WPS_MESSAGES_STATE_2 = ['Attempt:', '{}/15'.format(counter)]
        WPS_MESSAGES_CONFIG_RESET = ['Resetting', 'Config']
        WPS_MESSAGES_SUCCESS = ['Connected!', '']

        while ((self.network_manager.check_internet_connection() is False) and (self.network_manager.check_wifi_connection_via_arp_cache() is False)):
            # We have neither internet nor neighbours in arp cache

            state = counter % 2 == 1
            if (state):
                messages = WPS_MESSAGES_STATE_1
            else:
                messages = WPS_MESSAGES_STATE_2

            if counter < 8:
                self.connection_mode(established=False,
                                     state=state,
                                     attempt_count=counter,
                                     messages=messages)
            elif counter <= 10:
                self.connection_mode(established=False,
                                     state=1,
                                     attempt_count=counter,
                                     messages=WPS_MESSAGES_CONFIG_RESET)
            elif counter > 10 and counter <= 15:
                self.connection_mode(established=False,
                                     state=state,
                                     attempt_count=counter,
                                     messages=messages)
            else:
                # reboot tut gut
                self.reboot()

            is_connected = self.network_manager.initiate_wps()
            if is_connected:
                # Break this loop

                print('This was a triumph!')
                self.connection_mode(established=True,
                                     state=1,
                                     attempt_count=counter,
                                     messages=WPS_MESSAGES_SUCCESS)
                self.network_manager.restart_wifi_interface()
                sleep(2)
                ##
                # This reboot is a workaround because the wifi interfaces do not properly
                # boot up after the driver change. A reboot fixes this, is unelegant however
                self.reboot()
                break
            sleep(5)

            if counter == 10:
                self.network_manager.reset_wpa_supplicant()
            if counter >= 15:
                self.network_manager.reset_wpa_supplicant_develop()

            counter = counter + 1

        # if used_wps:
            # wps connection was established without the wext driver. Use the wext driver from now on
            # self.network_manager.connect_wifi_post_wps()

    def display_update(self):
        did_update=False
        # TODO
        return did_update

    def pihole_update(self):
        did_update=False
        # TODO
        return did_update

    def boot(self):

        ##
        # We need to be connected to the wifi
        self.connection_check_with_wps()

        ##
        # Update this software package first
        if self.display_update():
            self.reboot()

        ##
        # Check for pihole updates and update if another sanctioned version is available
        # I ran into trouble by updating to new pihole versions shortly after they were released.
        # Therefore we first check the /versions/ directory for sanctioned / stable versions
        # and update to that releasebranch
        if self.pihole_update():
            self.reboot()

        ##
        # Check if we can access the pihole API via webtoken
        # The webtoken generated by the salted web interface password hash
        # -> It is missing if no password is set
        if not self.network_manager.api_available():
            # display message that user should use setup a password in web interface
            self.message_mode()
            print('No API Token available. No web password set?')

        self.network_manager.api_test()

    ##
    # Pihole Management
    def update(self):
        self.notify()

    def switch_mode(self, mode:MODE):
        if self.mode is not mode:
            self.mode = mode
            self.update()

    def intro_mode(self):
        self.switch_mode(MODE.INTRO)

    def connection_mode(self, established=False, state=0, attempt_count=0, messages=''):
        if self.mode is not MODE.CONNECTION:
            self.mode = MODE.CONNECTION
            self.current_message_dict = {'established': established,
                                         'state': state,
                                         'attempt_count': attempt_count,
                                         'messages': messages}
            self.update()
        else:
            self.current_message_dict['established'] = established
            self.current_message_dict['state'] = state
            self.current_message_dict['attempt_count'] = attempt_count
            self.current_message_dict['messages'] = messages

    def clear_mode(self):
        self.switch_mode(MODE.CLEAR)

    def message_mode(self, message_type: MESSAGE_TYPE=MESSAGE_TYPE.INFO):
        self.current_message_dict = {'type': message_type,
                                     'messages':[]}
        if message_type == MESSAGE_TYPE.INFO:
            pass
        elif message_type == MESSAGE_TYPE.WARNING:
            pass
        elif message_type == MESSAGE_TYPE.ERROR:
            pass

        self.switch_mode(MODE.MESSAGE)

    def cycle_mode(self):
        self.switch_mode(MODE.CYCLE)

    def reboot_mode(self):
        self.switch_mode(MODE.REBOOT)

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

    def update_pihole_core(self):
        pass

    def update_ftl(self):
        pass

    def update_web(self):
        pass

    def check_update_for_module(self, module: PIHOLE_MODULE):
        pass
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

