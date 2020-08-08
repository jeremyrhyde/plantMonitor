#!/usr/bin/env python3
"""Sensor
"""

__author__ = "Sharan Juangphanich"
__copyright__ = "Copyright 2018, Latchables, Inc."
__credits__ = ["Sharan Juangphanich", "Aaron Sirken"]

import Adafruit_GPIO as GPIO
import time


class Lock_Sensor:

    _SENSOR_PIN = None
    _LED_PIN = None

    # Do not refer to the servo channels, refer to GPIO pin #
    def __init__(self, sensor_pin, led_pin):
        self._SENSOR_PIN = sensor_pin
        self._LED_PIN = led_pin

        self.gpio = GPIO.get_platform_gpio()

        self.gpio.setup(self._LED_PIN, GPIO.OUT)
        self.gpio.output(self._LED_PIN, GPIO.HIGH)


        self.gpio.setup(self._SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def close(self):
        self.gpio.cleanup()

    # Alternatively, an event detect may be used (add_event_detect)
    def is_Locked(self):
        a = self.gpio.input(self._SENSOR_PIN)
        #print(a)
        time.sleep(.2)
        b = self.gpio.input(self._SENSOR_PIN)
        #print(b)
        time.sleep(.2)
        c = self.gpio.input(self._SENSOR_PIN)
        #print(c)

        return not (a or b or c)

    def toggle_test(self):
        for i in range(100):
            self.gpio.output(self._LED_PIN, GPIO.HIGH)
            time.sleep(1)
            self.gpio.output(self._LED_PIN, GPIO.LOW)
            time.sleep(1)


def main():
    my_sensor = Lock_Sensor(20, 21)
    while True:
        print(my_sensor.is_Locked())
        time.sleep(1)
    #my_sensor.toggle_test()
    #my_sensor.close()



if __name__ == "__main__":
    main()
