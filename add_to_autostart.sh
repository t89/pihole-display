#!/bin/bash

# See https://stackoverflow.com/a/246128/3561275
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
    DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

script_name="run-pihole-display.sh"
auto_start_entry_available="$(sudo grep '$script_name' /etc/rc.local | wc -l)"
if [ ! "$auto_start_entry_available" -eq "0" ]; then
    echo "$script_name already in /etc/rc.local"
else
    # add to auto start
    sudo echo "sudo bash $DIR/$script_name &" >> /etc/rc.local
fi
