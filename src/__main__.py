#!/usr/bin/python

import os
from led_display import Display, MODE
from housekeeper import Housekeeper


def get_script_path():
    """ Returns path of script """
    return os.path.dirname(__file__)


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
        # housekeeper.loading_mode(activity_name='UPDATING', activity_detail='FIRMWARE')

        from time import sleep
        for i in range (1, 100):
            percentage = 1.0/100.0*i
            housekeeper.loading_mode(activity_name='UPDATING', activity_detail='FIRMWARE', percentage=percentage, activity_name_finished='UPDATE', activity_detail_finished='FINISHED')
            # print(percentage)
            sleep(0.2)

        housekeeper.loading_mode(activity_name='UPDATING', activity_detail='FIRMWARE', percentage=1.0, activity_name_finished='UPDATE', activity_detail_finished='FINISHED')



    except KeyboardInterrupt:
        print('Keyboard Interrupt detected: Exiting.')
        # Shut down display
        housekeeper.clear_mode()
        display.should_run = False
        # display.clear_display(refresh=True)
        display.join(5)


if __name__ == "__main__":
    main()
