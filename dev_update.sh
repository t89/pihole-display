#!/bin/bash

rm status_grabber.py
rm led_display.py
rm run.sh
rm location
rm known_clients
rm dev_update.sh

wget 192.168.100.181:8000/status_grabber.py
wget 192.168.100.181:8000/led_display.py
wget 192.168.100.181:8000/run.sh
wget 192.168.100.181:8000/location
wget 192.168.100.181:8000/known_clients
wget 192.168.100.181:8000/dev_update.sh
