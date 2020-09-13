import asyncio
import socket
import subprocess
from os import path
import time
import aiohttp

# from wireless import Wireless

from hole import Hole


class NetworkManager():
    """ Singleton """
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if NetworkManager.__instance is None:
            NetworkManager()
        return NetworkManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if NetworkManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            NetworkManager.__instance = self

        self.encoding = 'utf-8'
        self._api_token = None
        self._hole_ip = '127.0.0.1'
        self.loop = None

    def cmd(self, cmd):
        """ Run command in shell and return result """
        return subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT).stdout.read().decode(self.encoding)

    ##
    # WPS Connection
    # https://raspberrypi.stackexchange.com/a/80086/91158
    def initiate_wps(self):
        """ Initiates and handles the whole wps connection process """
        # -B = Background
        # -w = ?
        # -i = interface name
        # -c = path to configuration file

        # Shut down currently running wpa_supplicant
        cmd_kill_wpa = '''killall -q wpa_supplicant'''
        # Restart wpa_supplicant with correct config and driver
        cmd_fix_driver = '''wpa_supplicant -B w -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf'''
        # Attempt WPS connection
        cmd_use_wps = '''sudo wpa_cli -iwlan0 wps_pbc'''

        print('Shutdown current wpa_supplicant instance:')
        print(self.cmd(cmd_kill_wpa))
        time.sleep(3)

        print('Restart wpa_supplicant with WEXT driver:')
        print(self.cmd(cmd_fix_driver))

        print('Attempt WPS Process:')
        wps_command_feedback = self.cmd(cmd_use_wps)
        time.sleep(10)

        if 'ok' in wps_command_feedback.lower():
            # wps command execution was successful
            # check if the results have been positive
            return self.check_wps_success()
        return False

    def check_wps_success(self):
        """ Checks if the wps connection attempt was successful and returns bool """
        ##
        # Determining the success of the WPS connection attempt is kind of wonky:
        # If the attempt was successful if our wpa_supplicant.conf file will...
        # ...have been modified during the last ~20ish seconds
        # ...at least have one network={...} entry

        # CAREFUL: getctime() behaves differently than one may think:
        # https://docs.python.org/3/library/os.path.html#os.path.getctime
        wpa_supplicant_path = '/etc/wpa_supplicant/wpa_supplicant.conf'

        # Threshold in seconds
        modified_threshold = 20
        now_timestamp = time.time()

        try:
            modified_timestamp = path.getctime(wpa_supplicant_path)
            is_modified = (now_timestamp - modified_timestamp <= modified_threshold)

        except OSError as exc:
            # File not found or not accessible
            print(exc)

        # grep regex network and count each line it appeared in
        cmd_count_network_entries = '''grep -i "^network=" {} | wc -l'''.format(wpa_supplicant_path)
        value = self.cmd(cmd_count_network_entries)
        try:
            network_entry_count = int(value)
        except ValueError as exc:
            network_entry_count = 0
            print(exc)

        return (is_modified and network_entry_count > 0)

    def connect_wifi_post_wps(self):
        # -B = Background
        # -w = ?
        # -i = interface name
        # -D = Driver
        # -c = path to configuration file

        cmd_kill_wpa ='''killall -q wpa_supplicant'''
        cmd = '''wpa_supplicant -B w -D wext -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf'''

        print(self.cmd(cmd_kill_wpa))
        time.sleep(3)
        print(self.cmd(cmd))

    def restart_wifi_interface(self):
        # Stop existing WPA_Supplicant Process with Old Config
        print(self.cmd('killall -q wpa_supplicant'))
        time.sleep(3)

        # restart wlan0 interface
        print(self.cmd('sudo ip link set wlan0 down'))
        time.sleep(1)
        print(self.cmd('sudo ip link set wlan0 up'))

        ##
        # Old-school alternative
        # self.cmd('sudo wpa_action wlan0 stop')
        # self.cmd('sudo wpa_action wlan0 reload')
        # self.cmd('/sbin/ifup wlan0')

    def reset_wpa_supplicant_develop(self):
        import datetime
        timestamp_string = str(datetime.datetime.now()).replace(':', '').replace('-', '').replace(' ', '')
        original_name = 'wpa_supplicant.conf'
        replacement_name = 'wpa_supplicant_{}'.format(timestamp_string)

        # do not delete, but rename original wpa_supplicant.conf
        cmd_1 = '''sudo mv /etc/wpa_supplicant/{} /etc/wpa_supplicant/{}'''.format(original_name, replacement_name)
        cmd_2 = '''sudo cp /etc/wpa_supplicant/wpa_supplicant_backup.conf /etc/wpa_supplicant/wpa_supplicant.conf'''
        print('Rename original wpa_supplicant:\n{} -> {}'.format(original_name, replacement_name))
        print(self.cmd(cmd_1))
        print('Copy WPS compatible backup config to /etc/wpa_supplicant/wpa_supplicant.conf')
        print(self.cmd(cmd_2))

    def reset_wpa_supplicant(self):
        """ Rename the current wpa_supplicant.conf file and copy a wps-compatible file as a replacement """

        import datetime
        timestamp_string = str(datetime.datetime.now()).replace(':', '').replace('-', '').replace(' ', '')
        original_name = 'wpa_supplicant.conf'
        replacement_name = 'wpa_supplicant_{}'.format(timestamp_string)

        # do not delete, but rename original wpa_supplicant.conf
        cmd_1 = '''sudo mv /etc/wpa_supplicant/{} /etc/wpa_supplicant/{}'''.format(original_name, replacement_name)

        ##
        # REFACTOR / HARDCODED PATH
        # now copy blank sample conf to location
        cmd_2 = '''sudo cp /home/pi/pihole-display/utility/wpa_supplicant_wps.conf /etc/wpa_supplicant/wpa_supplicant.conf'''
        print('Rename original wpa_supplicant:\n{} -> {}'.format(original_name, replacement_name))
        print(self.cmd(cmd_1))
        print('Copy WPS compatible backup config to /etc/wpa_supplicant/wpa_supplicant.conf')
        print(self.cmd(cmd_2))

    def check_internet_connection(self, host="8.8.8.8", port=53, timeout=3):
        """
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as exc:
            print(exc)
            return False

    def get_mac_address(self):
        """ Returns devices Mac Address """
        import uuid
        return hex(uuid.getnode())

    def check_wifi_connection_via_arp_cache(self):
        # Checks arp cache for neighbour count
        cmd = 'ip neigh | wc -l'
        neighbour_count = self.cmd(cmd)
        print('NEIGHBOUR COUNT: {}'.format(neighbour_count))
        try:
            if (int(neighbour_count) > 0):
                return True
            else:
                return False
        except ValueError as exc:
            print(exc)
            return False

    # def check_wifi_connection_via_wireless(self):
    #     # Uses the wireless module to check wifi connection
    #           return (self.get_current_wifi_ssid is not None)

    def get_current_wifi_ssid(self):
        # wifi = Wireless()
        # # return wifi.current()
        # return wifi.driver()
        pass

    def emergency_fix_wifi(self):
        """ Attempt to fix Wifi connection, if it's switched off for some reason """
        # https://github.com/joshvillbrandt/wireless/issues/34
        cmd = 'sudo ifconfig wlan0 up'
        print(self.cmd(cmd))

    def get_local_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_ip = None
        try:
            # doesn't even have to be reachable
            sock.connect(('10.255.255.255', 1))
            local_ip = sock.getsockname()[0]
        except Exception as exc:
            print(exc)
        finally:
            sock.close()

        return local_ip

    def api_available(self):
        self.refresh_api_token()
        return (self._api_token is not None) and (self._api_token != '')

    def refresh_api_token(self):
        self._api_token = None
        token_variable_name = 'WEBPASSWORD='
        ##
        # If switching to awk:
        # Remember to escape {} with {{}} so that format does not throw a KeyError
        cmd = '''grep "{}" /etc/pihole/setupVars.conf | cut -f2 -d"="'''.format(token_variable_name)
        token_string = self.cmd(cmd)
        # print('Raw Token: {}'.format(token_string))
        self._api_token = token_string.replace(token_variable_name, '')
        # print('Stripped Token: {}'.format(self._api_token))

    async def pihole_stats(self):
        """Get the data from a *hole instance."""
        pihole_data = {}
        async with aiohttp.ClientSession() as session:
            data = Hole(self._hole_ip, self.loop, session)

            await data.get_versions()
            # version = json.dumps(data.data, indent=4, sort_keys=True)
            pihole_data['version'] = data.data

            await data.get_data()
            # pihole_data = json.dumps(data.data, indent=4, sort_keys=True)
            pihole_data['stats'] = data.data
            # Get the raw data
            # print("Status:", data.status)
            # print("Domains being blocked:", data.domains_being_blocked)
            return pihole_data

    def api_test(self):
        self.refresh_api_token()

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.pihole_stats())
        # self.loop.run_until_complete(self.disable())
        # self.loop.run_until_complete(self.enable())
        print('api_available: {}'.format(self.api_available()))
        # print('get_current_wifi_ssid: {}'.format(self.get_current_wifi_ssid()))
        # print('check_wifi_connection_via_wireless: {}'.format(self.check_wifi_connection_via_wireless()))
        print('check_wifi_connection_via_arp_cache: {}'.format(self.check_wifi_connection_via_arp_cache()))
        print('check_internet_connection: {}'.format(self.check_internet_connection()))


    async def disable(self):
        """Get the data from a *hole instance."""
        async with aiohttp.ClientSession() as session:
            data = Hole(self._hole_ip, self.loop, session, api_token=self._api_token)
            print(data)
            await data.disable()

    async def enable(self):
        """Get the data from a *hole instance."""
        async with aiohttp.ClientSession() as session:
            data = Hole(self._hole_ip, self.loop, session, api_token=self._api_token)
            await data.enable()
