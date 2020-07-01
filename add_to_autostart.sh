#!/bin/bash

echo "Run as super user"

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
    # delete last line (exit 0) from rc.local
    sudo sed -i '$d' /etc/rc.local > /dev/null 2>&1

    # add to auto start
    sudo echo "bash $DIR/$script_name &" >> /etc/rc.local
    sudo echo "exit 0" >> /etc/rc.local

    sudo chmod +x /etc/rc.local
fi
