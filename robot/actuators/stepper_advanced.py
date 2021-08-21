#!/usr/bin/env python3
"""Stepper
"""

import RPi.GPIO as GPIO
import time
from queue import *
import threading

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

        self._q = Queue()
        self._stop_event = threading.Event()

        self.motor_init_time = 0.05
        self.motor_step_delay = motor_step_delay

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

        self._disableDriver()

        self.stepper_thread = threading.Thread(target=self._stepper_run)
        self.stepper_thread.start()

        self.switch =  Limit_Switch_Sensor(self.limit_switch_pin, True)


        self.calibration()
        self.pos = 0

    # --------------------------------------------------------------------------

    def _enableDriver(self):
        GPIO.output(self.enable_pin, GPIO.LOW)

    def _disableDriver(self):
        GPIO.output(self.enable_pin, GPIO.HIGH)

    def _set_step_delay(self, motor_step_delay):
        self.motor_step_delay = motor_step_delay

    def _stepper_run(self):
        while not self._stop_event.is_set():
            command = self._q.get()
            self.move(command[0], command[1])
            #self.logger.info('hiiiiii ' + str(command))
            self._q.task_done()

    def release_motor(self):
        self._disableDriver()

    # --------------------------------------------------------------------------

    def queue_move(self, dist, disable = True):
        self._q.put([dist,disable])


    def move(self, desired_pos, disable = True):

        if disable: self._enableDriver()

        #desired_pos = self.pos + dist
        dist = desired_pos - self.pos
        i = self.pos

        if dist < 0:
            GPIO.output(self.dir_pin, False)

            while i > desired_pos and not self._kill and self.switch.state:
                self._movement()
                i = i + 1
        else:
            GPIO.output(self.dir_pin, True)

            while i < desired_pos and not self._kill and self.switch.state:
                self._movement()
                i = i + 1

        self.pos = self.pos + i

        if not self.switch.state: self.bounce_back()

        if disable: self._disableDriver()

    def stop_motor(self):
        self._kill = 1

    # --------------------------------------------------------------------------

    # def move_stepper(self, dist, disable = True):
    #
    #     if disable: self._enableDriver()
    #
    #     if dist < 0:
    #         GPIO.output(self.dir_pin, False)
    #     else:
    #         GPIO.output(self.dir_pin, True)
    #
    #     i = 0
    #     while i < abs(dist):
    #         GPIO.output(self.step_pin, GPIO.HIGH)
    #         time.sleep(self.motor_step_delay)
    #         GPIO.output(self.step_pin, GPIO.LOW)
    #         time.sleep(self.motor_step_delay)
    #         i = i + 1
    #
    #     if disable: self._disableDriver()

    def bounce_back(self):
        GPIO.output(self.dir_pin, True)

        while not self.switch.state:
            self._movement()

        self.pos = 0

    def _movement(self):
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(self.motor_step_delay)
        GPIO.output(self.step_pin, GPIO.LOW)
        time.sleep(self.motor_step_delay)


    def calibration(self, disable = True):

        time.sleep(1)

        if disable: self._enableDriver()

        GPIO.output(self.dir_pin, False)
        while self.switch.read_output_state(): self._movement()
        self.bounce_back()

        if disable: self._disableDriver()

    # --------------------------------------------------------------------------

def main():
    #stepper = Stepper(step_pin = 6, dir_pin = 5, enable_pin = 0, limit_switch_pin = 19)
    stepper = Stepper(step_pin = 20, dir_pin = 21, enable_pin = 16, limit_switch_pin = 13)#, motor_step_delay=0.0001)
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
            stepper.queue_move(int(user_input))
        elif user_input[0] == 'S':
            stepper._set_step_delay(float(user_input[1:]))
        else:
            pass


if __name__ == "__main__":
    main()
