#!/usr/bin/env python3
"""led.py
"""

import random
import time
import board
import neopixel

class LEDS:

    LED_PIN = board.D18
    ORDER = neopixel.GRB

    def __init__(self, num = 6):

        self.pixels = neopixel.NeoPixel(self.LED_PIN, num, brightness=0.2, auto_write=False, pixel_order=ORDER)

    def _brightness(self, percentage):
        self.pixels.brightness(percentage)


    def set_uniform_color(self, color):

        rgb_value = (0,0,0)

        if color == 'Warm':
            rgb_value = (255, 244, 229)
        elif color == 'Standard':
            rgb_value = (244, 255, 250)
        elif color == 'CoolWhite':
            rgb_value = (212, 235, 255)
        elif color == 'FullSpectrum':
            rgb_value = (255, 244, 242)
        elif color == 'GrowLight':
            rgb_value = (255, 239, 247)
        elif color == 'BlackLight':
            rgb_value = (167, 0, 255)

        self.pixels.fill(rgb_value)


    def set_grow_lights(self):

        for i in range(0, self.LED_PIN):
            r = random.random()
            if r > 0.7:
                self.pixels[i] = (0,0,255)
            elif r > 0.5:
                self.pixels[i] = (0,255,0)
            else:
                self.pixels[i] = (255,0,0)


def main():
    led = LEDS(6)
    led.set_uniform_color('Warm')

if __name__ == "__main__":
    main()
