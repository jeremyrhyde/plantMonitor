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
    _state = 0

    # Do not refer to the servo channels, refer to GPIO pin #
    def __init__(self, limit_switch_pin):
        self._LIMIT_SWITCH_PIN = limit_switch_pin

        self._stop_event = threading.Event()

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self._LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.limit_switch_thread = threading.Thread(target=self._output_state)
        self.limit_switch_thread.start()

    # --------------------------------------------------------------------------

    @property
    def state(self):
        return self._state

    # Alternatively, an event detect may be used (add_event_detect)
    def read_output_state(self):
        input = GPIO.input(self._LIMIT_SWITCH_PIN)
        self._state = input
        return input

    def _output_state(self):
        while not self._stop_event.is_set():
            self._state  = GPIO.input(self._LIMIT_SWITCH_PIN)

    def close(self):
        self._stop_event.set()
        self.limit_switch_thread.join()
        GPIO.cleanup()

    # --------------------------------------------------------------------------
    
def main():

    limit_switch = Limit_Switch_Sensor(19)

    while True:
        input = limit_switch.read_output()
        print(input)
        time.sleep(.1)


if __name__ == "__main__":
    main()
