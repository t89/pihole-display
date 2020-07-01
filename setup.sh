#!/bin/sh

# Fixes backspace issues when using ssh
export TERM=linux

# If these two dont work, use sudo raspi-config > Interface Options and
# activate SPI / I2S manually

# Enable SPI
sudo sed -i 's/dtparam=spi=off/dtparam=spi=on/g' /boot/config.txt

# Enable i2s
sudo sed -i 's/dtparam=i2s_arm=off/dtparam=o2s_arm=on/g' /boot/config.txt

# create known_clients file
touch known_clients

# System upgrade
sudo apt-get update -y
sudo apt-get upgrade -y

sudo apt update -y
# full-upgrade is used in preference to a simple upgrade, as it also picks up any dependency changes that may have been made
sudo apt full-upgrade -y

# Detect network devices (arp)
sudo apt-get install net-tools

sudo apt install python3-pip -y

# Read system stats
sudo pip3 install psutil

# LED Display
sudo apt-get install libtiff5 -y
sudo apt-get install libopenjp2-7 -y
sudo pip3 install --upgrade adafruit-circuitpython-ssd1306

#RGB Display
sudo pip3 install --upgrade adafruit circuitpython-rgb-display

# Both
sudo pip3 install --upgrade adafruit-blinka spidev pillow
