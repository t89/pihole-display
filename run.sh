#!/bin/sh

git pull origin master

python3 ./led_display.py &
