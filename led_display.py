# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

from linux_metrics import cpu_stat
from status_grabber import StatusGrabber


def update_pihole_stats():
    """ Updates global pihole variables """

    # TODO: Refactor. Content of this file should become a class
    global ph_q_blocked, ph_q_total, ph_q_perc, ph_top_client, ph_uptime, ph_active_device_count, ph_known_client_count

    stat_grabber.refresh_pihole_stats()
    pihole_stats = stat_grabber.get_pihole_stats()

    ph_q_blocked  = pihole_stats['ratio'][0]
    ph_q_total    = pihole_stats['ratio'][1]
    ph_q_perc     = int(pihole_stats['today_percentage'])/100.0
    ph_top_client = pihole_stats['topclient'].replace('.lan', '')
    ph_uptime     = pihole_stats['uptime']
    ph_active_device_count = pihole_stats['active_device_count']
    ph_known_client_count = pihole_stats['known_client_count']

def draw_bar_horizontal(origin, size, percentage):
    """ Use draw to draw progress bars within provided dimensions """
    border_stroke = 1

    norm_percentage = max(min(1, percentage), 0)

    # print('Origin: {}    Size: {}'.format(origin, size))
    x1 = origin[0]
    y1 = origin[1]

    width = size[0]
    height = size[1]

    x2 = x1 + width
    y2 = y1 + height

    draw.rectangle((x1,
                    y1,
                    x2,
                    y2), fill=255)

    draw.rectangle((x1 + border_stroke,
                    y1 + border_stroke,
                    x2 - border_stroke,
                    y2 - border_stroke), fill=0)

    draw.rectangle((x1 + 2 * border_stroke,
                    y1 + 2 * border_stroke,
                    x1 + norm_percentage * (width - 2 * border_stroke),
                    y2 - 2 * border_stroke), fill=255)

def get_horizontal_offset(text, font, tick):
    text_width = draw.textsize(text=text, font=font)[0]
    if (text_width > width):
        # should scroll

        delta = text_width - width
        step_size = delta / max_fps * 2

        return (max_fps / 2 - tick) * step_size
    else:
        return 0

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

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
max_fps = 30
delay = 1.0/max_fps

# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font_path = './fonts/PressStart2P.ttf'
icon_font_path = './fonts/pixel_dingbats-7.ttf'

##
# Kept for reference
# small_font = ImageFont.load_default()

font_size = 8
small_font = ImageFont.truetype(font_path, font_size)
small_icon_font = ImageFont.truetype(icon_font_path, font_size)

full_size = 32
full_size_font = ImageFont.truetype(font_path, full_size)
full_size_icon_font = ImageFont.truetype(icon_font_path, full_size)

half_size = 16
half_size_font = ImageFont.truetype(font_path, half_size)
half_size_icon_font = ImageFont.truetype(icon_font_path, half_size)

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

stat_grabber = StatusGrabber()

# Config
swap_threshold    = 10
max_states        = 4
progressbar_width = 1
font_offset       = 0 # some fonts do not align properly
icon_font_offset  = -4 # some fonts do not align properly

# Calculated configuration
step_size = width/max_fps/swap_threshold

# State 0

ph_q_blocked  = 0
ph_q_total    = 0
ph_q_perc     = 0
ph_top_client = ''
ph_uptime     = ''
ph_active_device_count = ''
ph_known_client_count = ''

update_pihole_stats()

##
# State 1
time_string   = stat_grabber.get_time()
weather_line1 = ''
weather_line2 = ''
weather_icon  = ''


##
# Helper
last_swap_time = time.time()
current_state = 0
tick = 0
while True:
    now = time.time()
    time_delta = now - last_swap_time

    should_swap = False
    progress = time_delta / swap_threshold

    if time_delta >= swap_threshold:
        should_swap = True
        last_swap_time = now

    if should_swap:
        current_state = (current_state + 1) % max_states

        ##
        # Put heavy load tasks here. These get executed _once_ when the state is swapped
        if (current_state == 0):
            # pihole stats state
            stat_grabber.refresh_pihole_stats()

        elif (current_state == 1):
            # time state

            sun_icon = b'\xC5\xBD'.decode()
            rain_icon = b'\xC5\xA0'.decode()
            lightning_icon = b'\xC5\x92'.decode()
            cloud_icon = b'\xE2\x80\xB9'.decode()
            snow_icon = b'\x4B'.decode()
            clock_icon = b'\xC3\xAE'.decode()

            time_string = stat_grabber.get_time()
            weather = stat_grabber.get_weather()
            condition = weather['condition']
            # Round precipitation
            precipitation = round(float(weather['precipitation'][:-2]))
            weather_line1 = '{} {} {}'.format(condition, weather['temperature'], weather['humidity'])
            weather_line2 = '{} {}%({}mm)'.format(weather['wind'], weather['probability'], precipitation)

            if ('sun' in condition.lower()):
                weather_icon = sun_icon
            elif ('rain' in condition.lower()):
                weather_icon = rain_icon
            elif ('cloud' in condition.lower()):
                weather_icon = cloud_icon
            elif ('snow' in condition.lower()):
                weather_icon = snow_icon
            elif ('thunder' in condition.lower()) or ('storm' in condition.lower()):
                weather_icon = lightning_icon
            else:
                weather_icon = clock_icon

        elif (current_state == 2):
            # pihole stats
            update_pihole_stats()

    ##
    # House Keeping
    tick = (tick + 1) % max_fps

    # Clear Screen
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # State handling
    if (current_state == 1):
        # if (tick % 2 == 0):
        #     time_string = '{}'.format(time)
        # else:
        #     time_string = '{}'.format(time).replace(':',' ')


        draw.text((x + 30, font_offset), time_string, font=half_size_font, fill=255)
        draw.text((x, icon_font_offset), '{}'.format(weather_icon), font=half_size_icon_font, fill=255)
        draw.text((x, font_offset + half_size), weather_line1, font=small_font, fill=255)
        draw.text((x, font_offset + half_size + font_size), weather_line2, font=small_font, fill=255)

    elif (current_state == 2):
        draw.text((x, font_offset), '{}'.format('Blocked today:'), font=small_font, fill=255)

        origin = (0, font_size)
        size = (width - progressbar_width - 2, half_size - 2)
        draw_bar_horizontal(origin, size, ph_q_perc)

        draw.text((x, font_offset + half_size + font_size), '({}/{}'.format(ph_q_blocked, ph_q_total), font=small_font, fill=255)

    elif (current_state == 3):
        draw.text((x, font_offset), 'Top Client:', font=small_font, fill=255)
        # draw.text((x, font_offset + font_size), '{0:>15}'.format(ph_top_client), font=half_size_font, fill=255)
        offset = get_horizontal_offset(text=ph_top_client, font=half_size_font, tick=tick)
        draw.text((x + offset, font_offset + font_size), '{}'.format(ph_top_client), font=half_size_font, fill=255)

        draw.text((x, font_offset + half_size + font_size), 'Clients:', font=small_font, fill=255)
        draw.text((x, font_offset + half_size + font_size), '{0:>15}'.format('{}/{}'.format(ph_active_device_count, ph_known_client_count)), font=small_font, fill=255)
        # draw.text((x, font_offset + half_size), 'Uptime:', font=small_font, fill=255)
        # draw.text((x, font_offset + half_size + font_size), '{0:>15}'.format(ph_uptime[:-3]), font=small_font, fill=255)

    else:
        cpu_percentage = float(stat_grabber.get_cpu_load()[:-1])/100.0
        ram_percentage = float(stat_grabber.get_memory_percentage()[:-1])/100.0 # cut off percentage sign

        draw.text((x, font_offset), 'CPU: ', font=half_size_font, fill=255)
        draw.text((x, font_offset + half_size), 'RAM: ', font=half_size_font, fill=255)

        cpu_bar_origin = (width/2, 1)
        ram_bar_origin = (width/2, half_size + 1)

        bar_size = (width/2 - progressbar_width - 2, half_size-2)

        draw_bar_horizontal(cpu_bar_origin, bar_size, cpu_percentage)
        draw_bar_horizontal(ram_bar_origin, bar_size, ram_percentage)


    # Draw State Progress
    size = width*progress
    v_size = height*progress
    # draw.rectangle((0, 0, size, progressbar_width), outline=1, fill=255)
    # draw.rectangle((0, height-progressbar_width, size, height), outline=1, fill=255)
    draw.rectangle((width-progressbar_width, height-v_size, width, height), outline=1, fill=255)

    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(delay)
