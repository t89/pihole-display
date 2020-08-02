#!/usr/bin/env python
#
#  led_display.py
#  pihole-display
#
#  Created by Thomas Johannesmeyer (thomas@geeky.gent) on 25.06.2020
#  Copyright (c) 2020 www.geeky.gent. All rights reserved.
#
# TODO: Refactor. Content of this file should become a class


import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

from stat_grabber import StatGrabber


def update_pihole_stats():
    """ Updates global pihole variables """
    global PH_Q_BLOCKED, PH_Q_TOTAL, PH_Q_PERC, PH_TOP_CLIENT, PH_UPTIME, PH_ACTIVE_DEVICE_COUNT, PH_KNOWN_CLIENT_COUNT

    stat_grabber.refresh_pihole_stats()
    pihole_stats = stat_grabber.get_pihole_stats()

    PH_Q_BLOCKED = pihole_stats['ratio'][0]
    PH_Q_TOTAL = pihole_stats['ratio'][1]
    PH_Q_PERC = int(pihole_stats['today_percentage'])/100.0
    PH_TOP_CLIENT = pihole_stats['topclient'].replace('.lan', '')
    PH_UPTIME = pihole_stats['uptime']
    PH_ACTIVE_DEVICE_COUNT = pihole_stats['active_device_count']
    PH_KNOWN_CLIENT_COUNT = pihole_stats['known_client_count']

def draw_bar_horizontal(origin, size, percentage):
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

    draw.rectangle((x_1,
                    y_1,
                    x_2,
                    y_2), fill=255)

    draw.rectangle((x_1 + border_stroke,
                    y_1 + border_stroke,
                    x_2 - border_stroke,
                    y_2 - border_stroke), fill=0)

    draw.rectangle((x_1 + 2 * border_stroke,
                    y_1 + 2 * border_stroke,
                    x_1 + norm_percentage * (width - 2 * border_stroke),
                    y_2 - 2 * border_stroke), fill=255)

def get_horizontal_offset(text, font, TICK):
    """ Takes a text, a font and the current frame count (TICK) to
    generate an horizontal scrolling offset """

    text_width = draw.textsize(text=text, font=font)[0]
    if (text_width > width):
        # should scroll

        delta = text_width - width
        STEP_SIZE = delta / MAX_FPS * 2

        return (MAX_FPS / 2 - TICK) * STEP_SIZE

    return 0

##
# Instantiate actors
# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

##
# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height. Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

stat_grabber = StatGrabber()

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# LED display can render 30fps max
MAX_FPS = 30
DELAY = 1.0/MAX_FPS

# Move left to right keeping track of the current x position for drawing shapes.
# TODO: Refactor. Leftover from the initial sample code. Still needed?
x = 0

##
# Font Configuration
# Kept for reference
# SMALL_FONT = ImageFont.load_default()

FONT_PATH = './fonts/PressStart2P.ttf'
ICON_FONT_PATH = './fonts/pixel_dingbats-7.ttf'

FONT_SIZE = 8
SMALL_FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)
SMALL_ICON_FONT = ImageFont.truetype(ICON_FONT_PATH, FONT_SIZE)

FULL_SIZE = 32
FULL_SIZE_FONT = ImageFont.truetype(FONT_PATH, FULL_SIZE)
FULL_SIZE_ICON_FONT = ImageFont.truetype(ICON_FONT_PATH, FULL_SIZE)

HALF_SIZE = 16
HALF_SIZE_FONT = ImageFont.truetype(FONT_PATH, HALF_SIZE)
HALF_SIZE_ICON_FONT = ImageFont.truetype(ICON_FONT_PATH, HALF_SIZE)



# Config
SWAP_THRESHOLD    = 10 # time in seconds after which the next screen will be shown
SCREEN_COUNT      = 4
PROGRESSBAR_WIDTH = 1
FONT_OFFSET       = 0  # some fonts do not align properly
ICON_FONT_OFFSET  = -4 # some fonts do not align properly

# Calculated configuration
STEP_SIZE = width/MAX_FPS/SWAP_THRESHOLD

##
# State 0
PH_Q_BLOCKED = 0
PH_Q_TOTAL = 0
PH_Q_PERC = 0
PH_TOP_CLIENT = ''
PH_UPTIME = ''
PH_ACTIVE_DEVICE_COUNT = ''
PH_KNOWN_CLIENT_COUNT = ''

update_pihole_stats()

##
# State 1
TIME_STRING = stat_grabber.get_time()
WEATHER_LINE_1 = ''
WEATHER_LINE_2 = ''
WEATHER_ICON = ''

##
# Helper
LAST_SWAP_TIME = time.time()
CURRENT_STATE = 0
TICK = 0
while True:
    now = time.time()
    time_delta = now - LAST_SWAP_TIME

    should_swap = False
    progress = time_delta / SWAP_THRESHOLD

    if time_delta >= SWAP_THRESHOLD:
        should_swap = True
        LAST_SWAP_TIME = now

    if should_swap:
        CURRENT_STATE = (CURRENT_STATE + 1) % SCREEN_COUNT

        ##
        # Put heavy load tasks here. These get executed _once_ when the state is swapped
        if CURRENT_STATE == 0:
            # pihole stats state
            stat_grabber.refresh_pihole_stats()

        elif CURRENT_STATE == 1:
            # time state

            sun_icon = b'\xC5\xBD'.decode()
            rain_icon = b'\xC5\xA0'.decode()
            lightning_icon = b'\xC5\x92'.decode()
            cloud_icon = b'\xE2\x80\xB9'.decode()
            snow_icon = b'\x4B'.decode()
            clock_icon = b'\xC3\xAE'.decode()

            TIME_STRING = stat_grabber.get_time()
            weather = stat_grabber.get_weather()
            condition = weather['condition']
            # Round precipitation
            precipitation = round(float(weather['precipitation'][:-2]))
            WEATHER_LINE_1 = '{} {} {}'.format(condition, weather['temperature'], weather['humidity'])
            WEATHER_LINE_2 = '{} {}%({}mm)'.format(weather['wind'], weather['probability'], precipitation)

            if 'sun' in condition.lower():
                WEATHER_ICON = sun_icon
            elif 'rain' in condition.lower():
                WEATHER_ICON = rain_icon
            elif 'cloud' in condition.lower():
                WEATHER_ICON = cloud_icon
            elif 'snow' in condition.lower():
                WEATHER_ICON = snow_icon
            elif ('thunder' in condition.lower()) or ('storm' in condition.lower()):
                WEATHER_ICON = lightning_icon
            else:
                WEATHER_ICON = clock_icon

        elif CURRENT_STATE == 2:
            # pihole stats
            update_pihole_stats()

    ##
    # House Keeping
    TICK = (TICK + 1) % MAX_FPS

    # Clear Screen
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # State handling
    if CURRENT_STATE == 1:
        # if (TICK % 2 == 0):
        #     TIME_STRING = '{}'.format(time)
        # else:
        #     TIME_STRING = '{}'.format(time).replace(':',' ')

        wl1_h_offset = get_horizontal_offset(text=WEATHER_LINE_1, font=SMALL_FONT, TICK=TICK)
        wl2_h_offset = get_horizontal_offset(text=WEATHER_LINE_2, font=SMALL_FONT, TICK=TICK)

        draw.text((x + 30, FONT_OFFSET), TIME_STRING, font=HALF_SIZE_FONT, fill=255)
        draw.text((x, ICON_FONT_OFFSET), '{}'.format(WEATHER_ICON), font=HALF_SIZE_ICON_FONT, fill=255)
        draw.text((x + wl1_h_offset, FONT_OFFSET + HALF_SIZE), WEATHER_LINE_1, font=SMALL_FONT, fill=255)
        draw.text((x + wl2_h_offset, FONT_OFFSET + HALF_SIZE + FONT_SIZE), WEATHER_LINE_2, font=SMALL_FONT, fill=255)

    elif CURRENT_STATE == 2:
        blocked_today_header_string = 'Blocked today:'
        blocked_h_offset = get_horizontal_offset(text=blocked_today_header_string, font=SMALL_FONT, TICK=TICK)
        draw.text((x + blocked_h_offset, FONT_OFFSET), '{}'.format(blocked_today_header_string), font=SMALL_FONT, fill=255)

        origin = (0, FONT_SIZE)
        size = (width - PROGRESSBAR_WIDTH - 2, HALF_SIZE - 2)
        draw_bar_horizontal(origin, size, PH_Q_PERC)

        block_ratio_string = '({}/{}'.format(PH_Q_BLOCKED, PH_Q_TOTAL)
        block_ratio_h_offset = get_horizontal_offset(text=block_ratio_string, font=SMALL_FONT, TICK=TICK)
        draw.text((x + block_ratio_h_offset, FONT_OFFSET + HALF_SIZE + FONT_SIZE), block_ratio_string, font=SMALL_FONT, fill=255)

    elif CURRENT_STATE == 3:
        draw.text((x, FONT_OFFSET), 'Top Client:', font=SMALL_FONT, fill=255)
        # draw.text((x, FONT_OFFSET + FONT_SIZE), '{0:>15}'.format(PH_TOP_CLIENT), font=HALF_SIZE_FONT, fill=255)
        offset = get_horizontal_offset(text=PH_TOP_CLIENT, font=HALF_SIZE_FONT, TICK=TICK)
        draw.text((x + offset, FONT_OFFSET + FONT_SIZE), '{}'.format(PH_TOP_CLIENT), font=HALF_SIZE_FONT, fill=255)

        draw.text((x, FONT_OFFSET + HALF_SIZE + FONT_SIZE), 'Clients:', font=SMALL_FONT, fill=255)
        draw.text((x, FONT_OFFSET + HALF_SIZE + FONT_SIZE), '{0:>15}'.format('{}/{}'.format(PH_ACTIVE_DEVICE_COUNT, PH_KNOWN_CLIENT_COUNT)), font=SMALL_FONT, fill=255)
        # draw.text((x, FONT_OFFSET + HALF_SIZE), 'Uptime:', font=SMALL_FONT, fill=255)
        # draw.text((x, FONT_OFFSET + HALF_SIZE + FONT_SIZE), '{0:>15}'.format(PH_UPTIME[:-3]), font=SMALL_FONT, fill=255)

    else:
        cpu_percentage = float(stat_grabber.get_cpu_load())/100.0
        ram_percentage = float(stat_grabber.get_memory_percentage())/100.0 # cut off percentage sign

        draw.text((x, FONT_OFFSET), 'CPU: ', font=HALF_SIZE_FONT, fill=255)
        draw.text((x, FONT_OFFSET + HALF_SIZE), 'RAM: ', font=HALF_SIZE_FONT, fill=255)

        cpu_bar_origin = (width/2, 1)
        ram_bar_origin = (width/2, HALF_SIZE + 1)

        bar_size = (width/2 - PROGRESSBAR_WIDTH - 2, HALF_SIZE-2)

        draw_bar_horizontal(cpu_bar_origin, bar_size, cpu_percentage)
        draw_bar_horizontal(ram_bar_origin, bar_size, ram_percentage)


    # Draw State Progress
    size = width*progress
    v_size = height*progress
    # draw.rectangle((0, 0, size, PROGRESSBAR_WIDTH), outline=1, fill=255)
    # draw.rectangle((0, height-PROGRESSBAR_WIDTH, size, height), outline=1, fill=255)
    draw.rectangle((width-PROGRESSBAR_WIDTH, height-v_size, width, height), outline=1, fill=255)

    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(DELAY)
