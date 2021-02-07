#!/usr/bin/env python3
"""Sensor
"""

__author__ = "Sharan Juangphanich"
__copyright__ = "Copyright 2018, Latchables, Inc."
__credits__ = ["Sharan Juangphanich", "Aaron Sirken"]

import RPi.GPIO as GPIO
import time


class Limit_Switch_Sensor:

    _LIMIT_SWITCH_PIN = None

    # Do not refer to the servo channels, refer to GPIO pin #
    def __init__(self, limit_switch_pin):
        self._LIMIT_SWITCH_PIN = limit_switch_pin

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self._LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def close(self):
        GPIO.cleanup()

    # Alternatively, an event detect may be used (add_event_detect)
    def read_output(self):
        input = GPIO.input(self._LIMIT_SWITCH_PIN)
        return input

def main():

    limit_switch = Limit_Switch_Sensor(26)

    while True:
        input = limit_switch.read_output()
        print(input)
        time.sleep(.1)


if __name__ == "__main__":
    main()
