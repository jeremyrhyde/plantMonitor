#!/usr/bin/env python3
"""Stepper
"""

import RPi.GPIO as GPIO
import time


class CNC:
    # Initialise the PCA9685 using the default address (0x40).
    # Alternatively specify a different address and/or bus:
    # pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

    def __init__(self):#, res_pins = (24,23,22), step_size = 'Full'):

        self.stepper_x = Stepper(step_pin = 6, dir_pin = 5, enable_pin = 0, limit_switch_pin = 19)
        self.stepper_y = Stepper(step_pin = 20, dir_pin = 21, enable_pin = 16, limit_switch_pin = 13)

        self.curr_pos = [0, 0]

    def close(self):
        GPIO.cleanup()


    def set_pos(self, pos, logging = False):
        diff = [float(pos[0])- self.curr_pos[0],
                float(pos[1])- self.curr_pos[1]]

        self.stepper_x.move_stepper(diff[0])
        self.stepper_y.move_stepper(diff[1])

        self.curr_pos = pos

        print('position set to ' + str(self.curr_pos))


    # def set_pos_absolute(self, pos_abs, logging = False):
    #     #diff = [float(pos_abs[0])/100*self.X_max - self.curr_pos[0],
    #     #        float(pos_abs[1])/100*self.Y_max - self.curr_pos[1]]
    #
    #     self.stepper_x.move_stepper()
    #
    #     self.stepper_x.move_stepper()
    #
    #     print('position set to ' + str(self.curr_pos))


    def calibration(self, disable = True):

        print('Calibrating X...')
        self.stepper_x.calibration()
        self.curr_pos[0] = 0
        print('X calibration complete!')

        time.sleep(0.5)

        print('Calibrating Y...')
        self.stepper_y.calibration()
        self.curr_pos[1] = 0
        print('Y calibration complete!')


def main():
    #stepper = Stepper(step_pin = 6, dir_pin = 5, enable_pin = 0, limit_switch_pin = 19)
    cnc = CNC()
    while True:
        user_input = input('Position: ')
        if user_input == 'C':
            cnc.calibration()
        elif user_input[0] == '[':
            pos = [int(user_input[1:-1].split(',')[0]), int(user_input[1:-1].split(',')[1])]
            cnc.set_pos(pos)

if __name__ == "__main__":
    main()
