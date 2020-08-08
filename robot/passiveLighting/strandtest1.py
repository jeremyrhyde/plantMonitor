import time
from neopixel import *
import argparse
import sys
import os
import random

os.environ["PYTHONPATH"] = "/home/pi/Development/robot/plant_monitor/robot/rpi_ws281x/python/build/lib.linux-armv7l-2.7"
#sys.path.append("/home/pi/Development/robot/plant_monitor/robot/rpi_ws281x/python/build/lib.linux-armv7l-2.7")
# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def colorRandom(strip, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    color_list = [Color(255, 255, 255), Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255), Color(128, 128, 0), Color(128, 0, 128), Color(0, 128, 128)]

    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color_list[random.randint(0,5)])
        strip.show()
        time.sleep(wait_ms/1000.0)

def fullSpectrumRandom(strip, wait_ms=50):
    """Wipe color across display a pixel at a time."""

    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        strip.show()
        time.sleep(wait_ms/1000.0)

if __name__ == '__main__':
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    while True:
       colorWipe(strip, Color(255, 255, 255))  # Red wipe
       time.sleep(.5)
       fullSpectrumRandom(strip)
       time.sleep(.5)
