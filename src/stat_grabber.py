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
import json

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
        raw_stat_list = stat_string.split()

        try:
            stats['version_core'] = raw_stat_list[raw_stat_list.index('Core:')+1]
        except IndexError as exc:
            print(exc)
            stats['version_core'] = ''

        try:
            stats['version_web'] = raw_stat_list[raw_stat_list.index('Web:')+1]
        except IndexError as exc:
            print(exc)
            stats['version_web'] = ''

        try:
            stats['version_ftl'] = raw_stat_list[raw_stat_list.index('FTL:')+1]
        except IndexError as exc:
            print(exc)
            stats['version_ftl'] = ''

        try:
            stats['hostname'] = raw_stat_list[raw_stat_list.index('Hostname:')+1]
        except IndexError as exc:
            print(exc)
            stats['hostname'] = ''

        try:
            stats['uptime'] = raw_stat_list[raw_stat_list.index('Uptime:')+1]
        except IndexError as exc:
            print(exc)
            stats['uptime'] = ''

        try:
            stats['status'] = raw_stat_list[raw_stat_list.index('Pi-hole:')+1]
        except IndexError as exc:
            print(exc)
            stats['status'] = ''

        try:
            stats['known_client_count'] = raw_stat_list[raw_stat_list.index('(Leased:')+1]
        except IndexError as exc:
            print(exc)
            stats['known_client_count'] = ''

        try:
            stats['today_percentage'] = raw_stat_list[raw_stat_list.index('Today:')+1][:-1]
        except IndexError as exc:
            print(exc)
            stats['today_percentage'] = ''

        try:
            stats['blocking'] = raw_stat_list[raw_stat_list.index('(Blocking:')+1]
        except IndexError as exc:
            stats['blocking'] = ''
            print(exc)

        try:
            stats['ratio'] = (raw_stat_list[raw_stat_list.index('(Total:')+1],
                              raw_stat_list[raw_stat_list.index('(Total:')+3])
        except IndexError as exc:
            stats['ratio'] = ''
            print(exc)

        try:
            stats['topclient'] = self.check_replace_known_client(raw_stat_list[raw_stat_list.index('Client:')+1])
        except IndexError as exc:
            stats['topclient'] = ''
            print(exc)

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
        """ Loads complete weather data as json input """

        url = 'https://wttr.in/{}?format={}'.format(location, 'j1')

        try:
            response = requests.get(url)
            ##
            # Note to myself: response.text is not a function, while response.json() is
            complete_weather_dict = response.json()
            current_condition = complete_weather_dict['current_condition']
            # nearest_area = complete_weather_dict['nearest_area']
            # request =  complete_weather_dict['request']

            # weather =  complete_weather_dict['weather']
            # hourly = weather[0]['hourly']

            ##
            # current_condition
            # 'FeelsLikeC': '19',
            # 'FeelsLikeF': '66',
            # 'cloudcover': '0',
            # 'humidity': '100',
            # 'localObsDateTime': '2020-09-01 08:47 PM',
            # 'observation_time': '01:47 AM',
            # 'precipMM': '1.2',
            # 'pressure': '998',
            # 'temp_C': '19',
            # 'temp_F': '66',
            # 'uvIndex': '4',
            # 'visibility': '16',
            # 'weatherCode': '113',
            # 'weatherDesc': [{'value': 'Sunny'}],
            # 'weatherIconUrl': [{'value': ''}],
            # 'winddir16Point': 'W',
            # 'winddirDegree': '280',
            # 'windspeedKmph': '17',
            # 'windspeedMiles': '11'

            self.weather = current_condition[0]
        except subprocess.CalledProcessError as exc:
            print(exc)
            self.weather['status'] = str(exc)

    def load_weather(self):
        self.last_weather_check = time.time()

        ##
        # REFACTOR
        HARD_CODED_BASE_PATH = '/home/pi/pihole-display'
        location = ""
        with open('{}/location'.format(HARD_CODED_BASE_PATH), 'r', encoding='utf-8') as location_file:
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
