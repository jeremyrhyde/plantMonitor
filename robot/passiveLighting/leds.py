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

    def __init__(self, num = 5):
        self.num_pixels = num
        self.pixels = neopixel.NeoPixel(self.LED_PIN, num, brightness=0.2, auto_write=False, pixel_order=self.ORDER)

    def _brightness(self, percentage):
        self.pixels.brightness(percentage)

    def set_all_red(self):
        self.pixels.fill((255,0,0))

    def set_grow_lights(self):

        for i in range(0, self.num_pixels):
            r = random.random()
            if r > 0.7:
                self.pixels[i] = (0,0,255)
            elif r > 0.5:
                self.pixels[i] = (0,255,0)
            else:
                self.pixels[i] = (255,0,0)


def main():
    led = LEDS(5)
    led.set_all_red()

if __name__ == "__main__":
    main()
