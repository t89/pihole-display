#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
    DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

cd $DIR

# Update display software
# git fetch --all
# git reset --hard origin/master

while : ; do
    # Check if we are connected to the internet
    # Connection status is set to 0 ONLY if ping was successful
    echo "Checking connection"
    connection_status=$(ping -c 1 -q google.com >&/dev/null; echo $?)
    echo "Status (should be 0): $connection_status"

    # Break endless loop if connection is found
    if [ $connection_status -eq 0 ]; then
        echo "Connection found"
        break
    fi

    echo "No connection found, initializing WPS"
    sudo bash "./utility/wps_config.sh"

    echo "15 seconds pause before rechecking"
    sleep 15
done

git stash

if [ -f "$DIR/.develop" ]; then
    # use develop version instead of master
    git checkout develop
    git pull origin develop
else
    # use release version
    git checkout master
    git pull origin master
fi

# Run display software in background
python3 "$DIR/src/led_display.py" >> "../pihole-display.log" &

##
# Updating blocklists on the raspberry pi zero may take up to
# 20 minutes. This process should be initiation via the web
# administration manually

# Update pihole
# pihole -up

