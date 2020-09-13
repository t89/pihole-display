#!/bin/bash

rm src/stat_grabber.py
rm src/led_display.py
rm src/__main__.py
rm src/observer.py
rm src/housekeeper.py
rm src/network.py
rm location
rm known_clients
rm dev_update.sh
rm anim/intro.gif

wget 192.168.1.212:8000/src/stat_grabber.py -P ./src/
wget 192.168.1.212:8000/src/led_display.py -P ./src/
wget 192.168.1.212:8000/src/__main__.py -P ./src/
wget 192.168.1.212:8000/src/observer.py -P ./src/
wget 192.168.1.212:8000/src/housekeeper.py -P ./src/
wget 192.168.1.212:8000/src/network.py -P ./src/
wget 192.168.1.212:8000/location
wget 192.168.1.212:8000/known_clients
wget 192.168.1.212:8000/dev_update.sh
wget 192.168.1.212:8000/anim/intro.gif -P ./anim/
