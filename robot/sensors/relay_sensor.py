#!/usr/bin/env python3
"""Sensor
"""

__author__ = "Sharan Juangphanich"
__copyright__ = "Copyright 2018, Latchables, Inc."
__credits__ = ["Sharan Juangphanich", "Aaron Sirken"]

import Adafruit_GPIO as GPIO
import time


class Relay_Sensor:

    _RELAY_PIN = None
    _LED_PIN = None

    # Do not refer to the servo channels, refer to GPIO pin #
    def __init__(self, relay_pin):
        self._RELAY_PIN = relay_pin
        # addition pin definiteion for power???

        self.gpio = GPIO.get_platform_gpio()

        self.gpio.setup(self._RELAY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def close(self):
        self.gpio.cleanup()

    # Alternatively, an event detect may be used (add_event_detect)
    def read_output(self):
        input = self.gpio.input(self._RELAY_PIN)
        return input

    def read_variable_output(self):
        output = 1
        for i in range(5):
            output = output and int(self.read_output()) 
            time.sleep(.5)

        return output


relay = Relay_Sensor(20)

def main():

    while True:
        relay.read_output()
        time.sleep(1)


if __name__ == "__main__":
    main()
