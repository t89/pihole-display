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

def check_connection_mode(hk):
    WPS_MESSAGES_DEFAULT = ['NO CONNECTION', 'PRESS WPS BUTTON', 'ON YOUR ROUTER']
    WPS_MESSAGES_CONFIG_RESET = ['NO CONNECTION', 'NO WPS FOUND', 'RESET CONFIG']

    for idx in range(1,16):
        if idx < 8:
            hk.connection_mode(established=False,
                                    attempt_count=idx,
                                    messages=WPS_MESSAGES_DEFAULT)
        elif idx < 10:
            hk.connection_mode(established=False,
                                    attempt_count=idx,
                                    messages=WPS_MESSAGES_CONFIG_RESET)
        elif idx > 10 and idx < 15:
            hk.connection_mode(established=False,
                                    attempt_count=idx,
                                    messages=WPS_MESSAGES_DEFAULT)
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

        # housekeeper.clear_mode()
        # housekeeper.cycle_mode()

        # check_cycle_mode(housekeeper)
        # check_connection_mode(housekeeper)
        check_intro_mode(housekeeper)
        # check_progress_mode(housekeeper)

        # housekeeper.boot()


    except KeyboardInterrupt:
        print('Keyboard Interrupt detected: Exiting.')
        # Shut down display
        housekeeper.clear_mode()
        display.should_run = False
        # display.clear_display(refresh=True)
        display.join(5)


if __name__ == "__main__":
    main()
