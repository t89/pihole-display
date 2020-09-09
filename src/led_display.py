#!/usr/bin/env python
#
#  led_display.py
#  pihole-display
#
#  Created by Thomas Johannesmeyer (thomas@geeky.gent) on 25.06.2020
#  Copyright (c) 2020 www.geeky.gent. All rights reserved.
#

import time
import subprocess
import threading

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import os.path

from stat_grabber import StatGrabber
from observer import Observer, Subject

from enum import Enum

class MODE(Enum):
    CLEAR = 0
    BOOT = 1
    CYCLE = 2
    PROGRESS = 3
    WARNING = 4

class Display(Observer, threading.Thread):
    ##
    # Observer Interface
    def update(self, subject: Subject) -> None:
        """ React to subject updates """
        self.current_mode = subject.mode
        self.current_message_dict = subject.current_message_dict

    def __init__(self):
        ##
        # Initializes hardware and drawing interface
        self.init_display()

        ##
        # Condition for main loop
        self.should_run = False

        ##
        # Instance Variables

        # Observer Pattern
        self.current_mode = MODE.CLEAR
        self.current_message_dict = {}

        self.current_state = 0
        self.pihole_stats = {}

        self.init_fonts()
        self.init_pihole_stats()

        self.stat_grabber = StatGrabber()

        self.special_mode = 0

        # Super Init
        super(Display, self).__init__()

    def init_display(self):
        """ Display Configuration """
        ##
        # Instantiate actors
        # Create the I2C interface.
        self.i2c = busio.I2C(SCL, SDA)

        ##
        # Create the SSD1306 OLED class.
        # The first two parameters are the pixel width and pixel height. Change these
        # to the right size for your display!
        self.display = adafruit_ssd1306.SSD1306_I2C(128, 32, self.i2c)

        # LED display can render 30fps max
        self.max_fps = 30

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.display.width
        self.height = self.display.height
        self.image = Image.new('1', (self.width, self.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        # self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        self.clear_display(refresh=True)

    def init_pihole_stats(self):
        """ Initializes Pi-Hole stats """
        self.ph_q_blocked = 0
        self.ph_q_total = 0
        self.ph_q_perc = 0
        self.ph_top_client = ''
        self.ph_uptime = ''
        self.ph_active_device_count = ''
        self.ph_known_client_count = ''

    def init_fonts(self):
        """ Font Configuration """

        # Kept for reference
        # self.small_font = ImageFont.load_default()

        ##
        # REFACTOR
        HARD_CODED_BASE_PATH = '/home/pi/pihole-display'

        font_path = '{}/fonts/PressStart2P.ttf'.format(HARD_CODED_BASE_PATH)
        icon_font_path = '{}/fonts/pixel_dingbats-7.ttf'.format(HARD_CODED_BASE_PATH)

        self.small_font_size = 8
        self.small_font = ImageFont.truetype(font_path, self.small_font_size)
        self.small_icon_font = ImageFont.truetype(icon_font_path, self.small_font_size)

        self.full_font_size = 32
        self.full_font = ImageFont.truetype(font_path, self.full_font_size)
        self.full_icon_font = ImageFont.truetype(icon_font_path, self.full_font_size)

        self.half_font_size = 16
        self.half_font = ImageFont.truetype(font_path, self.half_font_size)
        self.half_icon_font = ImageFont.truetype(icon_font_path, self.half_font_size)

        ##
        # Some fonts to not align properly, therefore we specify offsets here
        self.font_offset = 0
        self.icon_font_offset = -4

    def update_pihole_stats(self):
        """ Updates global pihole variables """

        self.stat_grabber.refresh_pihole_stats()
        self.pihole_stats = self.stat_grabber.get_pihole_stats()

        self.ph_q_blocked = self.pihole_stats['ratio'][0]
        self.ph_q_total = self.pihole_stats['ratio'][1]
        self.ph_q_perc = int(self.pihole_stats['today_percentage'])/100.0
        self.ph_top_client = self.pihole_stats['topclient'].replace('.lan', '')
        self.ph_uptime = self.pihole_stats['uptime']
        self.ph_active_device_count = self.pihole_stats['active_device_count']
        self.ph_known_client_count = self.pihole_stats['known_client_count']

    def config_for_mode(self, mode: MODE):
        config = {}
        if MODE.BOOT:
            pass
        elif MODE.CLEAR:
            pass
        elif MODE.CYCLE:
            config = {'should_cycle' : True,
                      'state_count': 4,
                      'durations_for_state': [10, 15, 10, 10]}
        elif MODE.PROGRESS:
            pass
        elif MODE.WARNING:
            pass
        return config

    def draw_bar_horizontal(self, origin, size, percentage):
        """ Use draw to draw progress bars within provided dimensions """
        border_stroke = 1

        norm_percentage = max(min(1, percentage), 0)

        # print('Origin: {}    Size: {}'.format(origin, size))
        x_1 = origin[0]
        y_1 = origin[1]

        width = size[0]
        height = size[1]

        x_2 = x_1 + width
        y_2 = y_1 + height

        self.draw.rectangle((x_1,
                             y_1,
                             x_2,
                             y_2), fill=255)

        self.draw.rectangle((x_1 + border_stroke,
                             y_1 + border_stroke,
                             x_2 - border_stroke,
                             y_2 - border_stroke), fill=0)

        self.draw.rectangle((x_1 + 2 * border_stroke,
                             y_1 + 2 * border_stroke,
                             x_1 + norm_percentage * (width - 2 * border_stroke),
                             y_2 - 2 * border_stroke), fill=255)

    def get_horizontal_offset(self, text, font, tick):
        """ Takes a text, a font and the current frame count (tick) to
        generate an horizontal scrolling offset """

        text_width = self.draw.textsize(text=text, font=font)[0]

        if (text_width > self.width - 3):
            # should scroll

            delta = text_width - self.width
            step_size = delta / self.max_fps

            half_fps = self.max_fps / 2
            # return (half_fps - tick) * step_size - half_fps
            return -tick * step_size

        return 0

    def load_icon_with_name(self, name, size=(32, 32)):
        """ Loads bitmap / png icons by name from the 'icons' folder """
        img = Image.open(os.path.join('icons', name), mode='r').resize(size).convert('1')
        return img

    def clear_display(self, fill=0, refresh=False):
        """  Clear display """
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=fill)
        # self.display.fill(fill)

        if refresh:
            self.display.show()

    def weather_icon_for_condition(self, condition):
        """ Returns weather icon for condition """

        sun_icon = b'\xC5\xBD'.decode()
        rain_icon = b'\xC5\xA0'.decode()
        lightning_icon = b'\xC5\x92'.decode()
        cloud_icon = b'\xE2\x80\xB9'.decode()
        snow_icon = b'\x4B'.decode()
        clock_icon = b'\xC3\xAE'.decode()
        retry_icon = b'\xC3\xB5'.decode()
        error_icon = b'\x6E'.decode()
        qmark_icon = b'\x3F'.decode()
        warning_icon = b'\x21'.decode()
        fog_icon = b'\x22'.decode()
        clear_icon = b'\x52'.decode()
        wind_icon = b'\x43'.decode()

        if 'sun' in condition.lower():
            weather_icon = sun_icon
        elif 'error' in condition.lower():
            weather_icon = error_icon
        elif 'rain' in condition.lower():
            weather_icon = rain_icon
        elif ('cloud' in condition.lower()) or ('overcast' in condition.lower()):
            weather_icon = cloud_icon
        elif 'clear' in condition.lower():
            weather_icon = clear_icon
        elif 'snow' in condition.lower():
            weather_icon = snow_icon
        elif 'fog' in condition.lower():
            weather_icon = fog_icon
        elif 'wind' in condition.lower():
            weather_icon = wind_icon
        elif ('thunder' in condition.lower()) or ('storm' in condition.lower()):
            weather_icon = lightning_icon
        else:
            weather_icon = clock_icon

        return weather_icon

    def change_mode(self, mode: MODE):
        self.current_mode = mode

    def run(self):
        """ Display main loop with config and state machine """

        self.should_run = True

        # Delay inbetween loop calls
        delay = 1.0/self.max_fps

        # Config

        # time in seconds after which the next screen will be shown
        swap_threshold = 10
        screen_count = 4
        progressbar_width = 1

        # Calculated configuration
        step_size = self.width/self.max_fps/swap_threshold

        self.update_pihole_stats()

        ##
        # State 1
        time_string = self.stat_grabber.get_time()
        weather_line_1 = ''
        weather_line_2 = ''
        weather_icon = ''

        ##
        # Helper
        last_swap_time = time.time()
        self.current_state = 0
        tick = 0

        while self.should_run:
            ##
            # House Keeping

            # load config
            # config = self.config_for_mode(self.current_mode)

            # time in seconds after which the next screen will be shown
            # swap_threshold = config['durations_for_state'][self.current_state]

            # Clear Screen
            self.clear_display()

            now = time.time()
            time_delta = now - last_swap_time

            should_swap = False
            progress = time_delta / swap_threshold

            if time_delta >= swap_threshold:
                should_swap = True
                last_swap_time = now

            # if self.current_mode is MODE.CYCLE:
            #     pass
            # elif self.current_mode is MODE.BOOT:
            #     pass
            # elif self.current_mode is MODE.CLEAR:
            #     pass
            # elif self.current_mode is MODE.PROGRESS:
            #     pass
            # elif self.current_mode is MODE.WARNING:
            #     pass


            ##
            # State cycle
            if should_swap:
                self.current_state = (self.current_state + 1) % screen_count

                ##
                # Put heavy load tasks here. These get executed _once_ when the state is swapped
                if self.current_state == 0:
                    # pihole stats state
                    self.stat_grabber.refresh_pihole_stats()

                elif self.current_state == 1:
                    # time state

                    time_string = self.stat_grabber.get_time()
                    weather = self.stat_grabber.get_weather()
                    if (weather['connection'] is not True):
                        weather_line_1 = 'Weather service'
                        weather_line_2 = 'unreachable'
                        condition = 'error'

                    else:
                        condition = weather['weatherDesc'][0]['value']
                        # Round precipitation
                        precipitation = round(float(weather['precipMM'][:-2]))
                        wind = '{} {}km/h'.format(weather['winddir16Point'], weather['windspeedKmph'])
                        pressure = '{}hPa'.format(weather['pressure'])
                        # probability = '' if (weather['probability'] == '-') else '{}% '.format(weather['probability'])
                        weather_line_1 = '{} {}°C RH:{}%'.format(condition, weather['temp_C'], weather['humidity'])
                        weather_line_2 = '{} {}mm'.format(wind, precipitation)

                    weather_icon = self.weather_icon_for_condition(condition)

                elif self.current_state == 2:
                    # pihole stats
                    self.update_pihole_stats()

            # State handling
            if self.current_state == 1:
                # if (tick % 2 == 0):
                #     time_string = '{}'.format(time)
                # else:
                #     time_string = '{}'.format(time).replace(':',' ')

                wl1_h_offset = self.get_horizontal_offset(text=weather_line_1,
                                                            font=self.small_font,
                                                            tick=tick)
                wl2_h_offset = self.get_horizontal_offset(text=weather_line_2,
                                                            font=self.small_font,
                                                            tick=tick)

                self.draw.text((30, self.font_offset),
                                time_string,
                                font=self.half_font,
                                fill=255)
                self.draw.text((0, self.icon_font_offset), '{}'.format(weather_icon),
                                font=self.half_icon_font,
                                fill=255)
                self.draw.text((wl1_h_offset, self.font_offset + self.half_font_size),
                                weather_line_1,
                                font=self.small_font,
                                fill=255)
                self.draw.text((wl2_h_offset, self.font_offset + self.half_font_size + self.small_font_size),
                                weather_line_2,
                                font=self.small_font,
                                fill=255)

            elif self.current_state == 2:
                blocked_today_header_string = 'Blocked today:'
                blocked_h_offset = self.get_horizontal_offset(text=blocked_today_header_string,
                                                                font=self.small_font,
                                                                tick=tick)
                self.draw.text((blocked_h_offset, self.font_offset),
                                '{}'.format(blocked_today_header_string),
                                font=self.small_font,
                                fill=255)

                origin = (0, self.small_font_size)
                size = (self.width - progressbar_width - 2, self.half_font_size - 2)
                self.draw_bar_horizontal(origin, size, self.ph_q_perc)

                block_ratio_string = '({}/{}'.format(self.ph_q_blocked, self.ph_q_total)
                block_ratio_h_offset = self.get_horizontal_offset(text=block_ratio_string, font=self.small_font, tick=tick)
                self.draw.text((block_ratio_h_offset,
                                self.font_offset + self.half_font_size + self.small_font_size),
                                block_ratio_string,
                                font=self.small_font,
                                fill=255)

            elif self.current_state == 3:
                self.draw.text((0, self.font_offset),
                                'Top Client:',
                                font=self.small_font,
                                fill=255)
                # draw.text((x, self.font_offset + self.small_font_size), '{0:>15}'.format(self.ph_top_client), font=self.half_font, fill=255)
                offset = self.get_horizontal_offset(text=self.ph_top_client,
                                                    font=self.half_font,
                                                    tick=tick)
                self.draw.text((offset, self.font_offset + self.small_font_size),
                                '{}'.format(self.ph_top_client),
                                font=self.half_font,
                                fill=255)

                self.draw.text((0, self.font_offset + self.half_font_size + self.small_font_size),
                                'Clients:',
                                font=self.small_font,
                                fill=255)
                self.draw.text((0, self.font_offset + self.half_font_size + self.small_font_size),
                                '{0:>15}'.format('{}/{}'.format(self.ph_active_device_count,
                                                                self.ph_known_client_count)),
                                font=self.small_font,
                                fill=255)
                # draw.text((0, self.font_offset + self.half_font_size), 'Uptime:', font=self.small_font, fill=255)
                # draw.text((0, self.font_offset + self.half_font_size + self.small_font_size), '{0:>15}'.format(self.ph_uptime[:-3]), font=self.small_font, fill=255)

            else:
                cpu_percentage = float(self.stat_grabber.get_cpu_load())/100.0
                ram_percentage = float(self.stat_grabber.get_memory_percentage())/100.0 # cut off percentage sign

                self.draw.text((0, self.font_offset),
                                'CPU: ',
                                font=self.half_font,
                                fill=255)
                self.draw.text((0, self.font_offset + self.half_font_size),
                                'RAM: ',
                                font=self.half_font,
                                fill=255)

                cpu_bar_origin = (self.width/2, 1)
                ram_bar_origin = (self.width/2, self.half_font_size + 1)

                bar_size = (self.width/2 - progressbar_width - 2, self.half_font_size-2)

                self.draw_bar_horizontal(cpu_bar_origin, bar_size, cpu_percentage)
                self.draw_bar_horizontal(ram_bar_origin, bar_size, ram_percentage)

                # Draw State Progress
                size = self.width*progress
                v_size = self.height*progress
                # self.draw.rectangle((0, 0, size, progressbar_width), outline=1, fill=255)
                # self.draw.rectangle((0, height-progressbar_width, size, height), outline=1, fill=255)
                self.draw.rectangle((self.width-progressbar_width,
                                        self.height-v_size,
                                        self.width,
                                        self.height),
                                    outline=1,
                                    fill=255)

            # Display image.
            self.display.image(self.image)
            self.display.show()
            time.sleep(delay)

            ##
            # Post Loop House Keeping
            tick = (tick + 1) % self.max_fps

