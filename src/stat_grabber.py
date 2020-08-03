#
#  stat_grabber.py
#  pihole-display
#
#  Created by Thomas Johannesmeyer (thomas@geeky.gent) on 26.06.2020
#  Copyright (c) 2020 www.geeky.gent. All rights reserved.
#


import time
import subprocess
import requests
import psutil

from datetime import datetime

class StatGrabber():

    def __init__(self):
        self.encoding = 'utf-8'
        self.stats = {}

        self.weather = {}
        self.last_weather_check = time.time() - 9999
        self.load_weather()

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    def get_local_ip(self):
        cmd = "hostname -I | cut -d' ' -f1"
        return subprocess.check_output(cmd, shell=True).decode(self.encoding)

    def get_active_network_device_count(self):
        # TODO: If the arp table is not flushed from time to time, this implementation
        # will yield inaccurate results
        # ip -s -s neigh flush all
        # A different solution is probably the way to go
        cmd = "sudo arp -a | wc -l"
        active_device_count_string = subprocess.check_output(cmd, shell=True).decode(self.encoding)

        try:
            active_device_count = int(active_device_count_string)-1

        except ValueError:
            active_device_count = 0

        self.stats['active_device_count'] = active_device_count
        return active_device_count

    def get_cpu_load(self):
        return psutil.cpu_percent()

    def get_memory_percentage(self):
        return psutil.virtual_memory().percent

    def get_memory_ratio(self):
        # REFACTOR: Rename since ratio implies factor
        mem_dict = dict(psutil.virtual_memory()._asdict())
        used = mem_dict['used']/1024/1024        # used memory in MB
        total = mem_dict['total']/1024/1024      # total memory in MB
        return (round(used, 1), round(total, 1)) # tuple rounded to first decimal

    def get_disk_space(self):
        cmd = 'df -h | awk \'$NF=="/"{printf "%d/%d GB  %s", $3,$2,$5}\''
        return subprocess.check_output(cmd, shell=True).decode(self.encoding)

    def get_time(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        # return time.strftime("%T", time.localtime())
        return current_time

    def check_replace_known_client(self, client_id):
        try:
            with open('./known_clients', 'r', encoding='utf-8') as known_clients_file:
                for line in known_clients_file:
                    client_list = line.split()
                    if (client_id == client_list[0]):
                        return ' '.join(client_list[1:])
        except IOError as e:
            print(e)

        return client_id

    def refresh_pihole_stats(self):
        stats = {}
        cmd = "pihole -c -e"
        stat_string = subprocess.check_output(cmd, shell=True).decode(self.encoding)
        # print(stat_string)
        raw_stat_list               = stat_string.split()
        stats['version_core']       = raw_stat_list[raw_stat_list.index('Core:')+1]
        stats['version_web']        = raw_stat_list[raw_stat_list.index('Web:')+1]
        stats['version_ftl']        = raw_stat_list[raw_stat_list.index('FTL:')+1]
        stats['hostname']           = raw_stat_list[raw_stat_list.index('Hostname:')+1]
        stats['uptime']             = raw_stat_list[raw_stat_list.index('Uptime:')+1]
        stats['status']             = raw_stat_list[raw_stat_list.index('Pi-hole:')+1]
        stats['known_client_count'] = raw_stat_list[raw_stat_list.index('(Leased:')+1]
        stats['today_percentage']   = raw_stat_list[raw_stat_list.index('Today:')+1][:-1]
        stats['blocking']           = raw_stat_list[raw_stat_list.index('(Blocking:')+1]
        stats['ratio']              = (raw_stat_list[raw_stat_list.index('(Total:')+1],
                                     raw_stat_list[raw_stat_list.index('(Total:')+3])
        stats['topclient']          = self.check_replace_known_client(raw_stat_list[raw_stat_list.index('Client:')+1])

        self.stats = stats
        self.get_active_network_device_count()

    def get_pihole_stats(self):
        return self.stats

    def get_weather(self):
        # every 5 minutes
        if time.time() - self.last_weather_check >= 300:
            self.load_weather()

        return self.weather

    def load_weather_for_location(self, location):
        # c    Weather condition,
        # C    Weather condition textual name,
        # h    Humidity,
        # t    Temperature (Actual),
        # f    Temperature (Feels Like),
        # w    Wind,
        # l    Location,
        # m    Moonphase 🌑🌒🌓🌔🌕🌖🌗🌘,
        # M    Moonday,
        # p    precipitation (mm),
        # o    Probability of Precipitation,
        # P    pressure (hPa),

        # D    Dawn*,
        # S    Sunrise*,
        # z    Zenith*,
        # s    Sunset*,
        # d    Dusk*.

        weather_format_string = '%l,%C,%t,%h,%w,%p,%o,%P'
        url = 'https://wttr.in/{}?format="{}"'.format(location, weather_format_string)


        weather = {'status' : 'success',
                    'location' : '',
                    'condition' : '',
                    'temperature' : '0',
                    'humidity' : '0',
                    'wind' : '0',
                    'precipitation' : '0',
                    'probability' : '0'}

        try:
            response = requests.get(url)
            ##
            # Note to myself: response.text is not a function, while response.json() is
            weather_string = response.text
        except subprocess.CalledProcessError as e:
            print(e)
            weather['status'] = str(e)

        else:
            # in case of no-exception

            raw_weather_list = weather_string.split(',')

            rwl_count = len(raw_weather_list)
            if rwl_count == 0:
                weather['status'] = 'empty'
            elif rwl_count <= 2:
                ##
                # If an error happens it is the only response available
                # e.g.: ['Unknown location; please try ~49.187089', '-97.937622\n']
                weather['status'] = ' '.join(raw_weather_list).replace('\n', '')
            else:
                weather = {'location' : raw_weather_list[0],
                        'condition' : raw_weather_list[1],
                        'temperature' : raw_weather_list[2],
                        'humidity' : raw_weather_list[3],
                        'wind' : raw_weather_list[4],
                        'precipitation' : raw_weather_list[5],
                        'probability' : raw_weather_list[6].replace('\n','')}

            # If value is empty string, replace with zero-string instead
            if weather['temperature'] == '':
                weather['temperature'] = '0'

            if weather['humidity'] == '':
                weather['humidity'] = '0'

            if weather['wind'] == '':
                weather['wind'] = '0'

            if weather['probability'] == '':
                weather['probability'] = '0'

            if weather['precipitation'] == '':
                weather['precipitation'] = '0'

            weather['wind'] = self.replace_arrows_in_string(weather['wind'])

            self.weather = weather

    def load_weather(self):
        self.last_weather_check = time.time()

        location = ""
        with open('../location', 'r', encoding='utf-8') as location_file:
            ##
            # TODO: Fix this sh*t u lzy bstrd
            for line in location_file:
                location = line.replace('\n', '').replace(' ', '+')
                break

        self.load_weather_for_location(location)

    def replace_arrows_in_string(self, s):
        """ Fix missing arrow chars from weather service in font PressStart2P """

        default_leftwards_arrow = b'\xE2\x86\x90'.decode()
        default_upwards_arrow = b'\xE2\x86\x91'.decode()
        default_downwards_arrow = b'\xE2\x86\x93'.decode()
        default_rightwards_arrow = b'\xE2\x86\x92'.decode()
        default_northwest_arrow = b'\xE2\x86\x96'.decode()
        default_northeast_arrow = b'\xE2\x86\x97'.decode()
        default_southwest_arrow = b'\xE2\x86\x99'.decode()
        default_southeast_arrow = b'\xE2\x86\x98'.decode()

        fixed_leftwards_arrow = b'\xE2\x86\x90'.decode()
        fixed_upwards_arrow = b'\xE2\x86\x91'.decode()
        fixed_downwards_arrow = b'\xE2\x86\x93'.decode()
        fixed_rightwards_arrow = b'\xE2\x86\x92'.decode()
        fixed_northwest_arrow = b'\xE2\x86\x91\xE2\x86\x90'.decode()
        fixed_northeast_arrow = b'\xE2\x86\x91\xE2\x86\x92'.decode()
        fixed_southwest_arrow = b'\xE2\x86\x93\xE2\x86\x90'.decode()
        fixed_southeast_arrow = b'\xE2\x86\x93\xE2\x86\x92'.decode()

        default_arrows = [default_leftwards_arrow,
                          default_upwards_arrow,
                          default_downwards_arrow,
                          default_rightwards_arrow,
                          default_northwest_arrow,
                          default_northeast_arrow,
                          default_southwest_arrow,
                          default_southeast_arrow]

        fixed_arrows = [fixed_leftwards_arrow,
                        fixed_upwards_arrow,
                        fixed_downwards_arrow,
                        fixed_rightwards_arrow,
                        fixed_northwest_arrow,
                        fixed_northeast_arrow,
                        fixed_southwest_arrow,
                        fixed_southeast_arrow]

        for idx, _ in enumerate(default_arrows):
            s = s.replace(default_arrows[idx], fixed_arrows[idx])

        return s
