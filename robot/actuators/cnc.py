#!/usr/bin/env python3
"""Servo
"""

import Adafruit_PCA9685

# Configure min and max servo pulse lengths
SERVO_MIN = 150#250  # Min pulse length out of 4096
SERVO_MAX = 600#500  # Max pulse length out of 4096


def pulse_map(angle):
    pulse = SERVO_MIN + (angle / 180) * (SERVO_MAX - SERVO_MIN)
    return int(pulse)


class Servo:
    # Initialise the PCA9685 using the default address (0x40).
    # Alternatively specify a different address and/or bus:
    # pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
    def __init__(self):
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(60)#(50)

    def set(self, pin, position):
        #print(position)
        self.pwm.set_pwm(pin, 0, position)

    def detach(self, pin):
        self.pwm.set_pwm(pin, 0, 4096)
