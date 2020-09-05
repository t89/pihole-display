#!/bin/bash

echo "Checking Web / Admin"

read -r destination_version < admin-version
current_version="$(pihole -v -a | awk '{print $4;}')"

if [[ $current_version == *"release/"* ]]; then
    # Already on a release branch
    current_version=$(echo "$current_version" | cut --delimiter='/' --fields=2)
fi

if [[ $current_version == *"v"* ]]; then
    # String still contains 'v' before version
    current_version=$(echo "$current_version" | cut --delimiter='v' --fields=2)
fi

if [[ $destination_version == *"v"* ]]; then
    # String still contains 'v' before version
    destination_version=$(echo "$destination_version" | cut --delimiter='v' --fields=2)
fi

# Compares two version strings and returns True if first version is greater than second
function version { echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }'; }

if [ "$(version "$destination_version")" -gt "$(version "$current_version")" ]; then
    # Outdated version > Need to update
    echo "Installed version $current_version is outdated."
    echo "Updating to $destination_version."

    pihole checkout web "release/v$destination_version"
else
    echo "Installed version $current_version is up to date"
fi

