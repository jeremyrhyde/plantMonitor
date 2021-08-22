#!/usr/bin/env python3
"""Stepper
"""

import RPi.GPIO as GPIO
import time
import math

from stepper_advanced import Stepper

class CNC_Controller:
    # Initialise the PCA9685 using the default address (0x40).
    # Alternatively specify a different address and/or bus:
    # pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
    curr_pos = [0, 0]

    X_MAX = 3250
    Y_MAX = 750

    def __init__(self, logger = None):
        self.logger = logger

        self.stepper_x = Stepper(step_pin = 6, dir_pin = 5, enable_pin = 0, limit_switch_pin = 19, motor_step_delay=0.0006, calibration=False)
        self.stepper_y = Stepper(step_pin = 20, dir_pin = 21, enable_pin = 16, limit_switch_pin = 13, motor_step_delay=0.0006, calibration=False)

        self.calibration_advanced()

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

    @property
    def get_pos(self):
        return self.curr_pos

    def move_line(self, pos, abs = False):
        if abs:
            move_pos = [int(pos[0]/100*self.X_MAX), int(pos[1]/100*self.Y_MAX)]
            self.stepper_x.queue_move(move_pos[0])
            self.stepper_y.queue_move(move_pos[1])
        else:
            self.stepper_x.queue_move(pos[0])
            self.stepper_y.queue_move(pos[1])

        time.sleep(.1)

        #print('{} : {}'.format(self.stepper_x._complete,self.stepper_y._complete))
        self.move_wait()
        self.curr_pos = [self.stepper_x.pos, self.stepper_y.pos]

        print('DONE: ' + str(self.curr_pos))


    def move_circle(self, r, theta1, theta2, abs = False):

        dtheta = 10

        start_x = int(self.curr_pos[0] + r*math.cos(math.radians(theta1)))
        start_y = int(self.curr_pos[1] + r*math.sin(math.radians(theta1)))

        self.stepper_x.queue_move(start_x)
        self.stepper_y.queue_move(start_y)
        self.move_wait()
        #self.curr_pos = [self.stepper_x.pos, self.stepper_y.pos]

        #print('DONE: ' + str(self.curr_pos))

        while theta1 < theta2:

            move_x = int(self.curr_pos[0] + r*math.cos(math.radians(theta1)))
            move_y = int(self.curr_pos[1] + r*math.sin(math.radians(theta1)))
            print('MOVE: [{},{}], ({})'.format(move_x, move_y, theta1))

            #self.stepper_x.queue_move(move_x)
            #self.stepper_y.queue_move(move_y)
            #self.move_wait()
            #self.curr_pos = [self.stepper_x.pos, self.stepper_y.pos]

            #print('DONE: [{},{}], ({})'.format(self.stepper_x.pos, self.stepper_y.pos, theta1))

            theta1 = theta1 + dtheta

            #time.sleep(5)


        self.stepper_x.queue_move(start_x)
        self.stepper_y.queue_move(start_y)

        self.move_wait()
        self.curr_pos = [self.stepper_x.pos, self.stepper_y.pos]


        time.sleep(.1)

        #print('{} : {}'.format(self.stepper_x._complete,self.stepper_y._complete))
        #self.move_wait()
        #self.curr_pos = [self.stepper_x.pos, self.stepper_y.pos]

        print('DONE: ' + str(self.curr_pos))

    # def set_pos(self, pos, logging = True):
    #     if not self.safe_move(pos):
    #         if self.logger: self.logger.info('Improper move...')
    #         return self.curr_pos
    #     else:
    #         diff = [int(pos[0])- self.curr_pos[0],
    #                 int(pos[1])- self.curr_pos[1]]
    #
    #         if self.logger and logging: self.logger.info('Move difference: [{},{}] -> POS: '.format(diff[0], diff[1]) + str(self.curr_pos))
    #
    #         self.stepper_x.move_stepper(diff[0])
    #         self.stepper_y.move_stepper(diff[1])
    #
    #         self.curr_pos = pos
    #
    #         #if logging: print('position set to ' + str(self.curr_pos))
    #
    #         return self.curr_pos
    #
    # def set_pos_abs(self, pos_abs, logging = True):
    #     if not self.safe_move_abs(pos_abs):
    #         if self.logger: self.logger.info('Improper move... (abs)')
    #         return self.curr_pos
    #     else:
    #         pos = [int(pos_abs[0]/100*self.X_MAX), int(pos_abs[1]/100*self.Y_MAX)]
    #         diff = [int(pos[0]) - self.curr_pos[0],
    #                 int(pos[1]) - self.curr_pos[1]]
    #
    #         if self.logger and logging: self.logger.info('Move difference: [{},{}] -> POS: '.format(diff[0], diff[1]) + str(self.curr_pos))
    #
    #
    #         self.stepper_x.move_stepper(diff[0])
    #
    #         self.stepper_y.move_stepper(diff[1])
    #
    #         self.curr_pos = pos
    #
    #         #if logging: print('position set to ' + str(self.curr_pos))
    #
    #         return self.curr_pos
    #
    #
    # def calibration(self, disable = True):
    #
    #     if self.logger: self.logger.info('Calibrating X...')
    #     self.stepper_x.calibration()
    #     self.set_pos_abs([0,0.5], False) # with additional bounce off
    #
    #     self.curr_pos[0] = 0
    #
    #     if self.logger: self.logger.info('X calibration complete!')
    #
    #     time.sleep(0.5)
    #
    #     if self.logger: self.logger.info('Calibrating Y...')
    #     self.stepper_y.calibration()
    #     self.set_pos_abs([0,2.5], False) # with additional bounce off
    #
    #     self.curr_pos[1] = 0
    #
    #     if self.logger: self.logger.info('Y calibration complete!')

    def move_wait(self):
        while not self.stepper_x._complete or not self.stepper_y._complete:
            #print('{} : {}'.format(self.stepper_x._complete,self.stepper_y._complete))
            time.sleep(0.1)

    def calibration_advanced(self, disable = True):

        if self.logger: self.logger.info('Starting calibrating...')
        self.stepper_x.queue_move('C')
        self.stepper_y.queue_move('C')

        time.sleep(.1)

        self.move_wait()
        self.curr_pos = [self.stepper_x.pos, self.stepper_y.pos]

        #self.curr_pos = [0,0]
        #print('HI: ' + str(self.curr_pos))

        if self.logger: self.logger.info('Calibration complete!')

def main():

    cnc = CNC_Controller()

    while True:
        user_input = input('COMMAND: ')
        if user_input == 'CAL':
            cnc.calibration_advanced()

        elif user_input=='CIRCLE':
            radius = input('Radius: ')
            theta1 = input('Theta1: ')
            theta2 = input('Theta2: ')
            cnc.move_circle(int(radius), int(theta1), int(theta2))

        elif user_input=='LINE':
            line_pos = input('Pos: ')
            pos = [int(line_pos[1:-1].split(',')[0]), int(line_pos[1:-1].split(',')[1])]
            cnc.move_line(pos, False)

        elif user_input=='ABS_LINE':
            line_pos = input('Abs Pos: ')
            pos = [int(line_pos[1:-1].split(',')[0]), int(line_pos[1:-1].split(',')[1])]
            cnc.move_line(pos, True)


if __name__ == "__main__":
    main()
