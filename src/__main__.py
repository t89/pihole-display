#!/usr/bin/python

import os
from led_display import Display, MODE
from housekeeper import Housekeeper
from time import sleep


def get_script_path():
    """ Returns path of script """
    return os.path.dirname(__file__)

def check_intro_mode(hk):
    hk.intro_mode()

def check_progress_mode(hk):
    # hk.loading_mode(activity_name='UPDATING', activity_detail='FIRMWARE')

    for i in range (1, 100):
        percentage = 1.0/100.0*i
        hk.loading_mode(activity_name='UPDATING',
                        activity_detail='FIRMWARE',
                        percentage=percentage,
                        activity_name_finished='UPDATE',
                        activity_detail_finished='FINISHED')
        # print(percentage)
        sleep(0.2)

    hk.loading_mode(activity_name='UPDATING',
                    activity_detail='FIRMWARE',
                    percentage=1.0,
                    activity_name_finished='UPDATE',
                    activity_detail_finished='FINISHED')

def check_cycle_mode(hk):
    hk.cycle_mode()

def check_reboot_mode(hk):
    hk.reboot_mode()

def check_connection_mode(hk):
    WPS_MESSAGES_STATE_1 = ['Press WPS button', 'on your router']
    WPS_MESSAGES_CONFIG_RESET = ['Resetting Config', '']

    for counter in range(1, 16):
        WPS_MESSAGES_STATE_2 = ['Attempt:', '{}/15'.format(counter)]
        state = counter % 2 == 1
        if (state):
            messages = WPS_MESSAGES_STATE_1
        else:
            messages = WPS_MESSAGES_STATE_2

        if counter < 8:
            hk.connection_mode(established=False,
                               state=state,
                               attempt_count=counter,
                               messages=messages)
        elif counter <= 10:
            hk.connection_mode(established=False,
                               state=state,
                               attempt_count=counter,
                               messages=WPS_MESSAGES_CONFIG_RESET)
        elif counter > 10 and counter < 15:
            hk.connection_mode(established=False,
                               state=state,
                               attempt_count=counter,
                               messages=messages)
        sleep(5)


def main():
    """ Greetings, Professor Falken... """
    try:
        cwd_path = os.getcwd()

        housekeeper = Housekeeper()
        display = Display()

        housekeeper.attach(display)

        # display.daemon = True
        display.start()

        housekeeper.boot()

        # housekeeper.clear_mode()
        housekeeper.cycle_mode()

        # check_reboot_mode(housekeeper)
        # check_cycle_mode(housekeeper)
        # check_connection_mode(housekeeper)
        # check_intro_mode(housekeeper)
        # check_progress_mode(housekeeper)


    except KeyboardInterrupt:
        print('Keyboard Interrupt detected: Exiting.')
        # Shut down display
        housekeeper.clear_mode()
        display.should_run = False
        # display.clear_display(refresh=True)
        display.join(5)


if __name__ == "__main__":
    main()
