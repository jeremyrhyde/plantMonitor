#!/usr/bin/env python3
"""Sensor
"""

__author__ = "Sharan Juangphanich"
__copyright__ = "Copyright 2018, Latchables, Inc."
__credits__ = ["Sharan Juangphanich", "Aaron Sirken"]

import RPi.GPIO as GPIO
import time
import threading

class Limit_Switch_Sensor:

    _LIMIT_SWITCH_PIN = None
    _state = 0

    # Do not refer to the servo channels, refer to GPIO pin #
    def __init__(self, limit_switch_pin, l_thread = True, verbose = False):
        self._LIMIT_SWITCH_PIN = limit_switch_pin

        self._stop_event = threading.Event()

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self._LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        if l_thread:
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
            if self.verbose: print(self._state)
            time.sleep(0.1)

    def close(self):
        self._stop_event.set()
        self.limit_switch_thread.join()
        GPIO.cleanup()

    # --------------------------------------------------------------------------

def main():

    limit_switch = Limit_Switch_Sensor(19, True, True)

    #while True:
    #    input = limit_switch.read_output()
    #    print(input)
    #    time.sleep(.1)

    user_input = input('Press Q to stop')

    limit_switch.close()


if __name__ == "__main__":
    main()
