#!/usr/bin/python

import os
import sys
from led_display import Display

def get_script_path():
    return os.path.dirname(__file__)

def main():
    try:
        cwd_path = os.getcwd()

        display = Display()

        display.run()

    except KeyboardInterrupt:
        print('Keyboard Interrupt detected: Exiting.')
        pass


if __name__ == "__main__":
    main()
