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

git stash
git pull origin master

# Run display software in background
python3 "$DIR/src/led_display.py" >> "../pihole-display.log" &

##
# Updating blocklists on the raspberry pi zero may take up to
# 20 minutes. This process should be initiation via the web
# administration manually

# Update pihole
# pihole -up

