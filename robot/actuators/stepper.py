#!/usr/bin/env python3
"""Stepper
"""

import RPi.GPIO as GPIO
import time

from limit_switch_sensor import Limit_Switch_Sensor

class Stepper:
    # Initialise the PCA9685 using the default address (0x40).
    # Alternatively specify a different address and/or bus:
    # pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
    _kill = 0


    def __init__(self, step_pin = 6, dir_pin = 5, enable_pin = 19, limit_switch_pin = 26, motor_step_delay=0.00125):
        #self.res_pins = res_pins#(14,15,18)
        self.step_pin = step_pin#21
        self.dir_pin = dir_pin#20
        self.enable_pin = enable_pin#16
        self.limit_switch_pin = limit_switch_pin

        #self.step_size = step_size

        self.motor_init_time = 0.05
        self.motor_step_delay = motor_step_delay

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

        self._disableDriver()

        self.switch =  Limit_Switch_Sensor(self.limit_switch_pin, True)

    def _enableDriver(self):
        GPIO.output(self.enable_pin, GPIO.LOW)

    def _disableDriver(self):
        GPIO.output(self.enable_pin, GPIO.HIGH)

    def _set_step_delay(self, motor_step_delay):
        self.motor_step_delay = motor_step_delay

    def move_stepper(self, dist, disable = True):

        if disable: self._enableDriver()

        if dist < 0:
            GPIO.output(self.dir_pin, False)
        else:
            GPIO.output(self.dir_pin, True)

        i = 0
        while i < abs(dist) and not self._kill and self.switch.state:
            print(self.switch.state)
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.motor_step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.motor_step_delay)
            i = i + 1

        if disable: self._disableDriver()

    def calibration(self, disable = True):

        time.sleep(1)

        if disable: self._enableDriver()

        GPIO.output(self.dir_pin, False)

        while self.switch.read_output_state():

            GPIO.output(self.step_pin, True)
            time.sleep(self.motor_step_delay)
            GPIO.output(self.step_pin, False)
            time.sleep(self.motor_step_delay)


        GPIO.output(self.dir_pin, True)

        while not self.switch.read_output_state():

            GPIO.output(self.step_pin, True)
            time.sleep(self.motor_step_delay)
            GPIO.output(self.step_pin, False)
            time.sleep(self.motor_step_delay)

        if disable: self._disableDriver()

    def release_motor(self):
        self._disableDriver()

def main():
    #stepper = Stepper(step_pin = 6, dir_pin = 5, enable_pin = 0, limit_switch_pin = 19)
    stepper = Stepper(step_pin = 20, dir_pin = 21, enable_pin = 16, limit_switch_pin = 13)
    while True:
        user_input = input('Position: ')

        if user_input == 'Q':
            stepper.release_motor()
            break
        elif user_input == 'R':
            stepper.release_motor()
        elif user_input == 'C':
            stepper.calibration()
        elif user_input.isdigit() or (user_input[0] == '-' and user_input[1:].isdigit()):
            stepper.move_stepper(int(user_input))
        elif user_input[0] == 'S':
            stepper._set_step_delay(float(user_input[1:]))
        else:
            pass


if __name__ == "__main__":
    main()
