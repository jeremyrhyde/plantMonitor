#!/usr/bin/env python3
"""Stepper
"""

import RPi.GPIO as GPIO
import time
#from RpiMotorLib import RpiMotorLib

#import sys

#sys.path.append('/home/pi/plantMonitor/robot/sensors')

#from limit_switch_sensor2 import Limit_Switch_Sensor

limit_switch = True

class Stepper:
    # Initialise the PCA9685 using the default address (0x40).
    # Alternatively specify a different address and/or bus:
    # pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

    def __init__(self, step_pin = 6, dir_pin = 5, enable_pin = 19, limit_switch_pin = 13):#, res_pins = (24,23,22), step_size = 'Full'):
        #self.res_pins = res_pins#(14,15,18)
        self.step_pin = step_pin#21
        self.dir_pin = dir_pin#20
        self.enable_pin = enable_pin#16
        self.limit_switch_pin = limit_switch_pin

        #self.step_size = step_size

        self.motor_init_time = 0.05
        self.motor_step_delay = 0.00125

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

        self._disableDriver()

        self.motor = None#RpiMotorLib.A4988Nema(self.dir_pin, self.step_pin, self.res_pins, 'A4988')
        self.curr_pos = 0

        self.total_rev = 0


        if limit_switch:
            GPIO.setup(self.limit_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _enableDriver(self):
        GPIO.output(self.enable_pin, GPIO.LOW)

    def _disableDriver(self):
        GPIO.output(self.enable_pin, GPIO.HIGH)

    def move_stepper2(self, disable = True):

        if disable: self._enableDriver()

        i = 0
        while i < 200:
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.motor_step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.motor_step_delay)
            i = i + 1

        if disable: self._disableDriver()

    def calibration(self, disable = True):

        #GPIO.output(self.enable_pin, False)
        if disable: self._enableDriver()

        while self.switch1.read_output():

            GPIO.output(self.dir_pin, False)
            GPIO.output(self.step_pin, True)
            time.sleep(self.motor_step_delay)
            GPIO.output(self.step_pin, False)
            time.sleep(self.motor_step_delay)

        while not self.switch1.read_output():

            GPIO.output(self.dir_pin, True)
            GPIO.output(self.step_pin, True)
            time.sleep(self.motor_step_delay)
            GPIO.output(self.step_pin, False)
            time.sleep(self.motor_step_delay)

        if disable: self._disableDriver()

        #self.curr_pos = 0 #degrees

    def read_output(self):
        input = GPIO.input(self.limit_switch_pin)
        return input

    def release_motor(self):
        self._disableDriver()

def main():
    stepper = Stepper(step_pin = 6, dir_pin = 5, enable_pin = 0, limit_switch_pin = 6)
    #stepper = Stepper(step_pin = 5, dir_pin = 0, enable_pin = 13, limit_switch_pin = 3)
    while True:
        user_input = input('Position: ')

        if user_input == 'Q':
            #stepper.move_stepper(numpad_cal['N'])
            stepper.release_motor()
            break
        elif user_input == 'R':
            stepper.release_motor()
        elif user_input == 'C':
            stepper.calibration()
            stepper.release_motor()
        elif user_input.isdigit():
            stepper.move_stepper2()
            #stepper.move_stepper(int(user_input))
        #elif user_input[1:].isdigit():
            #stepper.move_stepper(int(user_input[1:])*-1)


if __name__ == "__main__":
    main()