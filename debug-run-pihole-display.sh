#!/bin/bash

##
# TEMPORARY:
# Fix FTL Bug: https://github.com/pi-hole/PADD/issues/112#issuecomment-659540269
echo "4711" | sudo tee /var/run/pihole-FTL.port

# Run display software in background
python3 "$DIR/src/led_display.py"

##
# Updating blocklists on the raspberry pi zero may take up to
# 20 minutes. This process should be initiation via the web
# administration manually

# Update pihole
# pihole -up
