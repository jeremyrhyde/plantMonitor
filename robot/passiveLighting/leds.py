#!/usr/bin/env python3
"""led.py
"""

import RPi.GPIO as GPIO
import time

class LEDs:

    def __init__(self, pin = 14):
        self.led_pin = pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pin, GPIO.OUT)

    def turn_on(self):
        GPIO.output(21, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(21, GPIO.HIGH)

    def close(self):
        self.gpio.cleanup()


def main():
    led = LEDs()

    user_input = input('Enter 1 for on and 0 for off, else quit')
    while user_input == '1' or user_input == '0':
        if user_input == '1':
            led.turn_on()
        elif user_input == '0':
            led.turn_off()
        else:
            break

        user_input = input('Enter 1 for on and 0 for off, else quit')

    print('Closing LED')
    led.close()
    
if __name__ == "__main__":
    main()
