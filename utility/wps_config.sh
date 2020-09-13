#!/bin/bash

##
# Source:
# https://github.com/max2play/webinterface/blob/master/opt/max2play/wps_config.sh
# Make sure to activate WPS on Router before running this script
# Automatically sets up and saves WiFi Connection

# only run if there's no current wifi connection and WiFi is enabled
if [ "$(LANG=C && /sbin/ifconfig wlan0 | grep 'HWaddr\|ether' | wc -l)" -gt "0" -a "$(LANG=C && /sbin/ip addr show wlan0 | grep 'inet ' | grep -v '169.254' | wc -l)" -lt "1" ]; then
    killall -q wpa_supplicant
    sleep 1
    # Check if "update_config=1" needed in /opt/max2play/wpa_supplicant.conf for Autoconfig
    if [ "$(grep -i "update_config=1" /etc/wpa_supplicant/wpa_supplicant.conf | wc -l)" -lt "1" ]; then
        echo "update_config=1" >> /etc/wpa_supplicant/wpa_supplicant.conf
    fi

    # Make sure WPA-Supplicant is running with config
    # separate RPI3 no wext Driver for WPS!
    if [ "0" -lt "$(wpa_supplicant -h | grep nl80211 | wc -l)" ]; then
        wpa_supplicant -B w -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
    else
        wpa_supplicant -B w -D wext -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
    fi
    sleep 3

    # Clear network list
    for i in `wpa_cli -iwlan0 list_networks | grep ^[0-9] | cut -f1`; do wpa_cli -iwlan0 remove_network $i; done

    # get Routers supporting WPS, sorted by signal strength
    SSID=$(/sbin/wpa_cli -iwlan0 scan_results | grep "WPS" | sort -r -k3 | awk 'END{print $NF}')
    echo "Using $SSID for WPS"
    #SUCCESS=$(wpa_cli -iwlan0 wps_pbc $SSID)
    SUCCESS=$(wpa_cli -iwlan0 wps_pbc)
    sleep 10

    # Check for Entry in wpa_supplicant.conf
    VALIDENTRY=$(grep -i "^network=" /etc/wpa_supplicant/wpa_supplicant.conf | wc -l)

    # wpa_supplicant.conf should be modified in last 20 seconds by WPS Config
    MODIFIED=$(( `date +%s` - `stat -L --format %Y /etc/wpa_supplicant/wpa_supplicant.conf` ))

    if [ "$(echo "$SUCCESS" | grep 'OK' | wc -l)" -gt "0" -a "$VALIDENTRY" -gt "0" -a "$MODIFIED" -lt "20" ]; then
        # Now Config File should be written

        # Stop existing WPA_Supplicant Process with Old Config
        killall -q wpa_supplicant
        sleep 3

        # restart wlan0 interface
        sudo ip link set wlan0 down
        sudo ip link set wlan0 up

    else
        echo "ERROR creating connection"
        echo $SUCCESS
    fi
fi
