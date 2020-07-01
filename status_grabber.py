import time
import subprocess

from datetime import datetime

class StatusGrabber():

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

    def get_cpu_load(self):
        cmd = "top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'"
        return subprocess.check_output(cmd, shell=True).decode(self.encoding)

    def get_memory_percentage(self):
        cmd = "free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2 }'"
        return subprocess.check_output(cmd, shell=True).decode(self.encoding)

    def get_memory_usage(self):
        cmd = "free -m | awk 'NR==2{printf \"%s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        return subprocess.check_output(cmd, shell=True).decode(self.encoding)

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
        raw_stat_array            = stat_string.split()
        stats['version_core']     = raw_stat_array[raw_stat_array.index('Core:')+1]
        stats['version_web']      = raw_stat_array[raw_stat_array.index('Web:')+1]
        stats['version_ftl']      = raw_stat_array[raw_stat_array.index('FTL:')+1]
        stats['hostname']         = raw_stat_array[raw_stat_array.index('Hostname:')+1]
        stats['uptime']           = raw_stat_array[raw_stat_array.index('Uptime:')+1]
        stats['status']           = raw_stat_array[raw_stat_array.index('Pi-hole:')+1]
        stats['today_percentage'] = raw_stat_array[raw_stat_array.index('Today:')+1][:-1]
        stats['blocking']         = raw_stat_array[raw_stat_array.index('(Blocking:')+1]
        stats['ratio']            = (raw_stat_array[raw_stat_array.index('(Total:')+1],
                                     raw_stat_array[raw_stat_array.index('(Total:')+3])
        stats['topclient']        = raw_stat_array[raw_stat_array.index('Client:')+1]

        self.stats = stats

    def get_pihole_stats(self):
        return self.stats

    def get_weather(self):
        # every half-hour
        if (time.time() - self.last_weather_check >= 300):
            self.load_weather()

        return self.weather

    def load_weather(self):
        self.last_weather_check = time.time()

        location = ""
        with open('./location', 'r', encoding='utf-8') as location_file:
            ##
            # TODO: Fix this sh*t u lzy bstrd
            for line in location_file:
                location = line.replace('\n', '').replace(' ', '+')
                break

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
        cmd = 'curl wttr.in/{}?format="{}"'.format(location, weather_format_string)

        try:
            weather_string = subprocess.check_output(cmd, shell=True).decode(self.encoding)
        except subprocess.CalledProcessError as e:
            print(e)

        raw_weather_array = weather_string.split(',')

        weather = {'location' : raw_weather_array[0],
                   'condition' : raw_weather_array[1],
                   'temperature' : raw_weather_array[2],
                   'humidity' : raw_weather_array[3],
                   'wind' : raw_weather_array[4],
                   'precipitation' : raw_weather_array[5],
                   'probability' : raw_weather_array[6].replace('\n','')}

        # If probability is 0, an empty string is returned
        if (weather['probability'] is ''):
            weather['probability'] = '0'

        ##
        # Fix missing arrow chars in font PressStart2P
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
            weather['wind'] = weather['wind'].replace(default_arrows[idx], fixed_arrows[idx])

        self.weather = weather
