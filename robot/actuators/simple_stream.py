#!/usr/bin/env python
"""\
Simple g-code streaming script for grbl
Provided as an illustration of the basic communication interface
for grbl. When grbl has finished parsing the g-code block, it will
return an 'ok' or 'error' response. When the planner buffer is full,
grbl will not send a response until the planner buffer clears space.
G02/03 arcs are special exceptions, where they inject short line
segments directly into the planner. So there may not be a response
from grbl for the duration of the arc.
---------------------
The MIT License (MIT)
Copyright (c) 2012 Sungeun K. Jeon
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
---------------------
"""

import serial
import time
import os

#from limit_switch_sensor import Limit_Switch_Sensor
from multiprocessing import Process
import RPi.GPIO as GPIO
# Open grbl serial port
# s = serial.Serial('/dev/ttyACM0',115200)
#
# # Open g-code file
#
#
# # Wake up grbl
# s.write("\r\n\r\n".encode())
# time.sleep(2)   # Wait for grbl to initialize
# s.flushInput()  # Flush startup text in serial input

# Stream g-code to grb
class GRBL_Stream:

    def __init__(self, reset_pin, X_MAX, Y_MAX, serial_port = '/dev/ttyACM0', baud_rate = 115200):

        print('-------------------------')
        print('SYSTEM STARTING UP')
        print('-------------------------')

        print('Defining serial connection')
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.feedrate = 100

        self.serial = serial.Serial(serial_port,baud_rate, timeout=10)

        print('Setting parameters')
        self.curr_pos = [0,0]

        self.X_max = X_MAX
        self.Y_max = Y_MAX
        self.max_bonus = 0.1

        print('Initializing GPIOs')
        self._RESET_PIN = reset_pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._RESET_PIN, GPIO.OUT)
        GPIO.output(self._RESET_PIN, GPIO.LOW)

        print('-------------------------')
        self._reset()

        print('CNC SETUP...')
        self.init_cnc()

        self._send_line('$21=1')

        #self.calibrate()

        print('-------------------------')
        print('SYSTEM SETUP COMPLETE!')
        print('-------------------------')

    def init_cnc(self):
    #h = os.popen('pwd').read()
        #print(h)
        startup_file = open('/home/pi/plantmonitor/robot/actuators/startup.gcode','r')#'./robot/actuators/startup.gcode','r');

        print('Sending initializating command...')
        for line in startup_file:
            self._send_line(line)

        self._send_line('$21=1')
        startup_file.close()

    def close(self):
        self.serial.close()

    def set_feedrate(self, feedrate):
        self.feedrate = feedrate

    def get_feedrate(self):
        return self.feedrate

    def get_pos(self):
        return self.curr_pos

    def set_pos(self, pos):
        diff = [float(pos[0])- self.curr_pos[0],
                float(pos[1])- self.curr_pos[1]]

        self.send_move_cmd('X', str(float(diff[0])))

        self.send_move_cmd('Y', str(float(diff[1])))

        print('position set to ' + str(pos))

    def set_pos_absolute(self, pos_abs):
        diff = [float(pos_abs[0])/100*self.X_max - self.curr_pos[0],
                float(pos_abs[1])/100*self.Y_max - self.curr_pos[1]]

        self.send_move_cmd('X', str(float(diff[0])))

        self.send_move_cmd('Y', str(float(diff[1])))

        print('position set to ' + str(pos))


    def _reset(self):
        #GPIO.setup(self._RESET_PIN, GPIO.OUT)
        print('Reseting CNC')
        GPIO.output(self._RESET_PIN, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(self._RESET_PIN, GPIO.LOW)
        time.sleep(4)


    def _handle_limit_hit(self, dir, check = True):

        #for i in range(0,100):
        #    self._send_line('$10')
        print(' - Limit switch detected! moving off')

        self._send_line('$21=0')
        self._reset()
        print('resetting')
        self._send_line('$21=0')

        try:
            if dir == 'Y':
                dist = '6.0'
                state = self.send_move_cmd('Y', dist, False) #Direction
            else:
                dist = '2'
                state = self.send_move_cmd('X', dist, False)
        except Exception as e:
            print('Improper2 position command: ' + str(e))

        if state:
            self._send_line('$21=1')
            self._send_line('$21=1')


    def calibrate_X(self):
        print('Calibrating X...')
        #for i in range(0,10):
        #    self.send_move_cmd('X', str('5'))

        no_limit_hit, pos = self.send_move_cmd('X', str(float(-1*self.X_max*(1 + self.max_bonus))))
        if no_limit_hit: self._handle_limit_hit('X')
        print('Calibrating of X complete!')


    def calibrate_Y(self):
        print('Calibrating Y...')
        no_limit_hit, pos = self.send_move_cmd('Y', str(float(-1*self.Y_max*(1 + self.max_bonus))))
        if no_limit_hit: self._handle_limit_hit('Y')
        print('Calibrating of Y complete!')

    def calibrate(self):

        print('Calibrating and returning to home...')

        self.calibrate_X()
        time.sleep(3)
        self.calibrate_Y()

        print('Homing complete position set to (0,0)')

    def limit_cycle(self, axis):

        state = self._send_line('$10=3')
        val = True

        while 'Reset' in state or 'ALARM' in state or 'unlock' in state or 'help' in state:
            print('BAD STATE: ' + str(state))
            val = False

            self._handle_limit_hit(axis)


            try:
                state = self._send_line('$10=3')
            except Exception as e:
                print('Improper command: ' + str(e))
                state = 'NONE'
                print('BAD STATE: ' + str(state))

        return val


    def send_move_cmd(self, axis, dist, check=True):

        # Set new position
        state = ''
        dist = -1*float(dist)
        next_pos = [0,0]

        if axis == 'X':
            next_pos[0] = self.curr_pos[0] - dist
        if axis == 'Y':
            next_pos[1] = self.curr_pos[1] - dist #since neg otherwsie switch pos
        print(str("[{:.1f}, {:.1f}]".format(float(next_pos[0]),float(next_pos[1]))))


        if next_pos[0] >= self.X_max or next_pos[1] >= self.Y_max:
            print('Error! Moving beyond max (' + axis + ')')
        else:
            cmd = axis + ' {:.1f} F {}'.format(dist, self.get_feedrate())
            print(' - Moving to ' + cmd)

            try:
                state = self._send_line('G21 G91 ' + cmd)
                self.curr_pos = next_pos
            except Exception as e:
                print('Improper position command: ' + str(e))
        #else:
        #    time.sleep(abs(float(dist))/5

        val = self.limit_cycle(axis)
        return val, next_pos

    def send_move_cmd_safe(self, axis, dist):

        # Set new position
        next_pos = self.curr_pos
        if axis == 'X':
            next_pos[0] = next_pos[0] + float(dist)
        if axis == 'Y':
            next_pos[1] = next_pos[1] + float(dist) #since neg otherwsie switch pos
        print('POS: ' + str(next_pos))
        # Check if move is safe
        if next_pos[0] >= self.X_max or next_pos[1] >= self.Y_max:
            print('Error! Moving beyond max (' + axis + ')')
        else:
            cmd = axis + dist + ' F' + str(self.get_feedrate())

            print(cmd)
            try:
                self._send_line('G21 G91 ' + cmd)
            except Exception as e:
                print('Improper position command: ' + str(e))


    def _send_line(self, line):
        l = line.strip() # Strip all EOL characters for consistency
        print('G-Code: ' + l)

        l = l + '\n'
        self.serial.write(l.encode()) # Send g-code block to grbl
        grbl_out_bytes = self.serial.readline() # Wait for grbl response with carriage return
        grbl_out = grbl_out_bytes.decode("UTF-8")

        if grbl_out.strip() == 'ok':
            state = 'Action Completed'
        else:
            state = 'Action Error: ' + grbl_out.strip()

        time.sleep(2)
        print(state)
        return state


# Wait here until grbl is finished to close serial port and file.
def main():

    X_MAX = 22
    Y_MAX = 106
    reset_pin = 26

    cnc = GRBL_Stream(reset_pin, X_MAX, Y_MAX)

    while True:
        user_input = input('Input: ')
        if len(user_input) > 0:
            if user_input[0] == 'X' or user_input[0] == 'Y':
                distance = user_input[2:]
                axis = user_input[0]

                cnc.send_move_cmd(axis, distance)

            elif user_input[0] == 'F':
                user_feedrate = user_input[2:]
                try:
                    cnc.set_feedrate(int(user_feedrate))
                except:
                    print('Improper feedrate command')
            elif user_input[0] == 'C':
                cnc.calibrate()

            elif user_input[0] == '$':
                cnc._send_line(user_input)

            elif user_input[0] == '[':
                new_pos = user_input[1:-1].split(',')
                cnc.set_pos_absolute(new_pos)

            elif user_input == 'Reset':
                cnc._reset()

            elif user_input[0] == 'Q':
                print('Closing out...')
                cnc.close()
                break
            else:
                print(user_input)
        else:
            print('Closing out...')
            cnc.close()
            break

if __name__ == "__main__":
    main()


# example: Y -0.5
