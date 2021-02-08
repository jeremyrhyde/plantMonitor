#!/usr/bin/env python3
"""Stepper
"""

import RPi.GPIO as GPIO
import time

from .stepper import Stepper

class CNC_Controller:
    # Initialise the PCA9685 using the default address (0x40).
    # Alternatively specify a different address and/or bus:
    # pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

    def __init__(self):

        self.stepper_x = Stepper(step_pin = 6, dir_pin = 5, enable_pin = 0, limit_switch_pin = 19, motor_step_delay=0.0006)
        self.stepper_y = Stepper(step_pin = 20, dir_pin = 21, enable_pin = 16, limit_switch_pin = 13, motor_step_delay=0.0006)

        self.curr_pos = [0, 0]

        self.X_MAX = 3250
        self.Y_MAX = 750

    def close(self):
        GPIO.cleanup()


    def safe_move(self, pos):
        if pos[0] <= self.X_MAX and pos[1] <= self.Y_MAX:
            return True
        return False

    def safe_move_abs(self, pos):
        if pos[0] <= 100 and pos[1] <= 100:
            return True
        return False


    def get_pos(self):
        return self.curr_pos


    def set_pos(self, pos, logging = False):
        if not self.safe_move(pos):
            if logging: print('Improper move...')
            return self.curr_pos
        else:
            diff = [int(pos[0])- self.curr_pos[0],
                    int(pos[1])- self.curr_pos[1]]

            self.stepper_x.move_stepper(diff[0])
            self.stepper_y.move_stepper(diff[1])

            self.curr_pos = pos

            if logging: print('position set to ' + str(self.curr_pos))

            return self.curr_pos

    def set_pos_abs(self, pos_abs, logging = False):
        if not self.safe_move_abs(pos_abs):
            if logging: print('Improper move... (abs)')
            return self.curr_pos
        else:
            pos = [int(pos_abs[0]/100*self.X_MAX), int(pos_abs[1]/100*self.Y_MAX)]
            diff = [int(pos[0]) - self.curr_pos[0],
                    int(pos[1]) - self.curr_pos[1]]

            self.stepper_x.move_stepper(diff[0])

            self.stepper_y.move_stepper(diff[1])

            self.curr_pos = pos

            if logging: print('position set to ' + str(self.curr_pos))

            return self.curr_pos


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
    cnc = CNC_Controller()

    while True:
        user_input = input('Position: ')
        if user_input == 'C':
            cnc.calibration()

        elif user_input[0] == '[':
            pos = [int(user_input[1:-1].split(',')[0]), int(user_input[1:-1].split(',')[1])]
            cnc.set_pos(pos)

        elif user_input[0] == '%':
            pos = [int(user_input[2:-1].split(',')[0]), int(user_input[2:-1].split(',')[1])]
            cnc.set_pos_abs(pos)


if __name__ == "__main__":
    main()
