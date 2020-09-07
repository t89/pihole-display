#!/bin/bash

rm src/stat_grabber.py
rm src/led_display.py
rm src/__main__.py
rm location
rm known_clients
rm dev_update.sh

wget 192.168.100.247:8000/src/stat_grabber.py -P ./src/
wget 192.168.100.247:8000/src/led_display.py -P ./src/
wget 192.168.100.247:8000/src/__main__.py -P ./src/
wget 192.168.100.247:8000/location
wget 192.168.100.247:8000/known_clients
wget 192.168.100.247:8000/dev_update.sh
