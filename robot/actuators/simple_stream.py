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

from limit_switch_sensor import Limit_Switch_Sensor
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

    def __init__(self, serial_port = '/dev/ttyACM0', baud_rate = 115200):

        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.feedrate = 100

        self.serial = serial.Serial(serial_port,baud_rate)

        self._RESET_PIN = 26
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._RESET_PIN, GPIO.OUT)
        GPIO.output(self._RESET_PIN, GPIO.LOW)

        self.init_cnc()

        self.curr_pos = [0,0]

        #self.calibrate()
        self.X_max = 20
        self.Y_max = 106

        print('Initializing limit switches (X : #1, Y : #1)')
        self.limit_switch_X = Limit_Switch_Sensor(26)
        self.limit_switch_Y = Limit_Switch_Sensor(26)

        self._send_line('$21=1')

    def init_cnc(self):
        startup_file = open('startup.gcode','r');

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

    def calibrate(self):

        print('Returning to home')
        self.calibrate_X()

        time.sleep(3)

        self.calibrate_Y()

    def calibrate_X(self):

        limit_val_X = self.limit_switch_X.read_output()

        print('Beginning to calibrate X axis...')

        # Calibrate X axis
        while limit_val_X:
            self.send_move_cmd('X', '0.05')

            limit_val_X = self.limit_switch_X.read_output()

        self.curr_pos[0] = 0

        print('Calibrate of X axis complete!')

    def calibrate_Y(self):

        print('Beginning to calibrate Y axis...')

        limit_val_Y = self.limit_switch_Y.read_output()
        print(limit_val_Y)
        # Calibrate Y axis
        while limit_val_Y:
            print('advance')
            self.send_move_cmd('Y', '0.1')

            limit_val_Y = self.limit_switch_Y.read_output()

            time.sleep(.02)
            print(limit_val_Y)
        self.curr_pos[1] = 0

        print('Calibrate of Y axis complete!')

    def limit_switch_process(self):

        while True:
            limit_val_Y = self.limit_switch_Y.read_output()

            if not limit_val_Y:
                self._send_line('M00')
                break

    def _reset(self):
        GPIO.setup(self._RESET_PIN, GPIO.OUT)
        GPIO.output(self._RESET_PIN, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(self._RESET_PIN, GPIO.LOW)


    def _handle_limit_hit(self, dir = 0):
        print('Limit switch detected! moving off')
        time.sleep(4)
        print('sending 1')
        self._send_line('$21=0')
        time.sleep(1)
        self._reset()
        time.sleep(3)
        self._send_line('$21=0')
        time.sleep(2)
        try:
            if dir == 0:
                state = self.send_move_cmd('Y', '-1.0')
            else:
                state = self.send_move_cmd('Y', '1.0')
        except Exception as e:
            print('Improper2 position command: ' + str(e))

            # if 'Reset' in str(e) or '9' in str(e) or 'unlock' in str(e):
            #     print('retrying with $21 reset')
            #     self._send_line('$21=0')
            #     time.sleep(2)
            #     if dir == 0:
            #         self.send_move_cmd('Y', '-0.2')
            #     else:
            #         self.send_move_cmd('Y', '0.2')
        if state:
            time.sleep(2)
            self._send_line('$21=1')


    def calibrate_Y2(self):

        self.send_move_cmd('Y', str(float(self.Y_max)))
        self._handle_limit_hit()
        self.send_move_cmd('X', str(float(self.X_max)))
        self._handle_limit_hit()
        #time.sleep(self.Y_max/10)
        #self._handle_limit_hit()
        # self.close()
        # self.init_cnc()
        # try:
        #     self._send_line('$21=0')
        # except Exception as e:
        #     print('Improper position command: ' + str(e))
        # self.close()
        # self.init_cnc()

    def send_move_cmd(self, axis, dist):
        cmd = axis + dist + ' F' + str(self.get_feedrate())

        print(cmd)
        try:
            state = self._send_line('G21 G91 ' + cmd)
        except Exception as e:
            print('Improper position command: ' + str(e))
        else:
            time.sleep(float(dist)/5)

            #if 'Reset' in str(e):
            #    self._handle_limit_hit()
        print('STATE:' + str(state))
        if 'Reset' in state or 'ALARM' in state or 'unlock' in state or 'help' in state:
            self._handle_limit_hit()
            return False
        return True

            #    print('retrying with $21 reset')
            #    self._send_line('$21=0')
            #    time.sleep(2)
            #    self.send_move_cmd(axis, dist)



    def send_move_cmd_safe(self, axis, dist):

        # Set new position
        next_pos = self.curr_pos
        if axis == 'X':
            next_pos[0] = next_pos[0] + float(dist)
        if axis == 'Y':
            next_pos[1] = next_pos[1] - float(dist) #since neg otherwsie switch pos

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
        print(state)
        return state


# Wait here until grbl is finished to close serial port and file.
def main():

    cnc = GRBL_Stream()

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
                cnc.calibrate_Y2()

            elif user_input[0] == '$' or user_input == 'Reset':
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
