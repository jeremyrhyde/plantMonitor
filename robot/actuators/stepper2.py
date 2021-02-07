#!/usr/bin/env python3
"""Stepper
"""

import RPi.GPIO as GPIO
import time
from RpiMotorLib import RpiMotorLib

#import sys

#sys.path.append('/home/pi/plantMonitor/robot/sensors')

from limit_switch_sensor import Limit_Switch_Sensor

limit_switch = True

class Stepper:
    # Initialise the PCA9685 using the default address (0x40).
    # Alternatively specify a different address and/or bus:
    # pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

    def __init__(self, step_pin = 6, dir_pin = 5, enable_pin = 19, limit_switch_pin = 26, res_pins = (24,23,22), step_size = 'Full'):
        self.res_pins = res_pins#(14,15,18)
        self.step_pin = step_pin#21
        self.dir_pin = dir_pin#20
        self.enable_pin = enable_pin#16
        self.limit_switch_pin = limit_switch_pin

        self.step_size = step_size

        self.motor_init_time = 0.05
        self.motor_step_delay = 0.00125

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

        self.motor = None#RpiMotorLib.A4988Nema(self.dir_pin, self.step_pin, self.res_pins, 'A4988')
        self.curr_pos = 0

        self.total_rev = 0


        if limit_switch:
            self.switch1 = Limit_Switch_Sensor(self.limit_switch_pin)


        #if inductor:
        #    self.inductor = Inductor()


    #def run_inductor(self):
    #    self.inductor.inductor_actuation()

    def _enableDriver(self):
        GPIO.output(self.enable_pin, False)

    def _disableDriver(self):
        GPIO.output(self.enable_pin, True)

    def vary_stepsize(self, stepsize):
        self.stepsize = stepsize

    def convert_degree_to_rev(self, delta_d):

        ang = abs(delta_d)

        if delta_d > 0:
            dir = False
        else:
            dir = True

        if self.step_size == 'Full':
            d = 1
        elif self.step_size == 'Half':
            d = 1
        elif self.step_size == '1/4':
            d = 4
        elif self.step_size == '1/8':
            d = 8

        rev = int(ang*200*d/360)

        return dir, rev

    def calculate_motion(self, desired_pos):
        delta_d = desired_pos - self.curr_pos

        #print('From: ' + str(self.curr_pos) + '    To: ' + str(desired_pos))

        dir, rev = self.convert_degree_to_rev(delta_d)

        if dir:
            self.total_rev = self.total_rev + rev
        else:
            self.total_rev = self.total_rev - rev

        #print(' --- Direction: ' + str(dir) + '    Revolutions: ' + str(rev))
        return dir, rev

    def move_stepper(self, desired_pos):

        dir, rev = self.calculate_motion(desired_pos)

        self._enableDriver()
        #print('Rev: {} Desired_pos: {} curr_pos: {} total_rev: {}'.format(rev, desired_pos, self.curr_pos, self.total_rev))
        self.motor.motor_go(dir, self.step_size, rev, self.motor_step_delay, False , self.motor_init_time)

        self.curr_pos = desired_pos


    def move_stepper2(self):
        i = 0
        while i < 200:
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.motor_step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            i = i + 1

    def calibration(self):

        GPIO.output(self.enable_pin, False)

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

        self.curr_pos = 0 #degrees

    def release_motor(self):
        GPIO.output(self.enable_pin, True)

def main():
    stepper = Stepper(step_pin = 9, dir_pin = 10, enable_pin = 11, limit_switch_pin = 6)
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
