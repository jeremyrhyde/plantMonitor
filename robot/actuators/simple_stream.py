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

        #self.cnc = GRBL_Stream()
        self.init_cnc()

        self.curr_pos = [0,0]

        #self.calibrate()
        self.X_max = 5
        self.Y_max = 5

        print('Initializing limit switches (X : #1, Y : #1)')
        self.limit_switch_X = Limit_Switch_Sensor(26)
        self.limit_switch_Y = Limit_Switch_Sensor(26)

    def init_cnc(self):
        startup_file = open('startup.gcode','r');

        print('Sending initializating command...')
        for line in startup_file:
            self._send_line(line)

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


    def calibrate_Y2(self):

        print('Beginning to calibrate Y2 axis...')

        p = Process(target=self.limit_switch_process)
        p.start()

        self.send_move_cmd('Y', '1.0')

        p.join()

        print('Calibrate of Y2 axis complete!')

    def send_move_cmd(self, axis, dist):
        cmd = axis + dist + ' F' + str(self.get_feedrate())

        print(cmd)
        try:
            self._send_line('G21 G91 ' + cmd)
        except Exception as e:
            print('Improper position command: ' + str(e))

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
            print('Action Completed')
        else:
            print('Action Error: ' + grbl_out.strip())


# Wait here until grbl is finished to close serial port and file.
def main():

    cnc = GRBL_Stream()
    cnc.calibrate_Y2()

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
