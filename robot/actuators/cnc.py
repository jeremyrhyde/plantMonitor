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

from .robot_config import *

# Stream g-code to grb
class GRBL_Stream:

    def __init__(self, serial_port = '/dev/ttyACM0', baud_rate = 115200):

        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.feedrate = 100

        self.serial = serial.Serial(serial_port,baud_rate)
        self.serial.write("\r\n\r\n".encode())
        time.sleep(2)   # Wait for grbl to initialize
        self.serial.flushInput()  # Flush startup text in serial input

        self.init()

        self.calibrate()

        self.curr_pos = [0,0]

    def init(self):
        startup_file = open('startup.gcode','r');

        print('Sending initializating command...')
        for line in startup_file:
            self.send_line(line)

        startup_file.close()

    def close(self):
        self.serial.close()

    def set_feedrate(self, feedrate):
        self.feedrate = feedrate

    def get_feedrate(self):
        return self.feedrate

    def send_line(self, line):
        l = line.strip() # Strip all EOL characters for consistency
        print('G-Code: ' + l)

        l = l + '\n'
        self.serial.write(l.encode()) # Send g-code block to grbl

    def line_response(self):
        grbl_out_bytes = self.serial.readline() # Wait for grbl response with carriage return
        grbl_out = grbl_out_bytes.decode("UTF-8")

        if grbl_out.strip() == 'ok':
            print('Action Completed')
        else:
            print('Action Error: ' + grbl_out.strip())

    def send_cmd(self, line):
        self.send_line(self, line)
        self.line_response()

    def move_to(self, move):

        check_bounds, bound_hit = self.check_move(move)

        bounded_move = create_bounded_move(move)

        new_pos = self.pos + bounded_move

        print('Moving to: ' = str(new_pos))

        # Send command and check
        line = self.convert_to_line(move)
        self.send_line(line)
        self.line_response() # check to make sure action complete

        # Send api altera on boundary box hit
        if check_bounds:
            api_alert = "Bad Move: Boundaries " + str(bound_hit)
            self.send_alert_API(api_alert)

        # Update position
        self.pos = new_pos

    def check_pos(self):
        if self.pos[0] > Y_MIN \
            and self.pos[0] < Y_MAX \
            and self.pos[1] > X_MIN \
            and self.pos[1] > X_MAX:
            return True

    def check_move(self, move):
        bounds_hit = []
        if self.pos[0] + move[0] < Y_MIN:
            print('Bound X0 Hit')
            bounds_hit.append('x0')
        if self.pos[0] + move[0] > Y_MAX:
            print('Bound X1 Hit')
            bounds_hit.append('x1')
        if self.pos[1] + move[1] < X_MIN:
            print('Bound Y0 Hit')
            bounds_hit.append('y0')
        if self.pos[1] + move[1] > X_MAX:
            print('Bound Y1 Hit')
            bounds_hit.append('y1')

        if len(bound_hit) > 0:
            return False, bound_hit
        else:
            return True, []

    #send api fucntion(Denoting move and errors)
    def send_alert_API(self, line):
        pass

    def create_bounded_move(self, move):
        boundary_x = 0
        boundary_y = 0

        bounded_move = move

        if self.pos[0] + move[0] < Y_MIN + boundary_y:
            bounded_move[0] = Y_MIN
        if self.pos[0] + move[0] > Y_MAX - boundary_y:
            bounded_move[0] = Y_MAX
        if self.pos[1] + move[1] < X_MIN + boundary_x:
            bounded_move[1] = X_MIN
        if self.pos[1] + move[1] > X_MAX - boundary_x:
            bounded_move[1] = X_MIN

        return bounded_move

    def calibrate(self):
        pass



# Wait here until grbl is finished to close serial port and file.
def main():
    cnc = GRBL_Stream()

    while True:
        user_input = input('Input: ')
        if len(user_input) > 0:
            if user_input[0] == 'X' or user_input[0] == 'Y':
                user_distance = user_input[2:]
                cmd = user_input[0] + user_distance + '.0 F' + str(cnc.get_feedrate())
                print(cmd)
                try:
                    cnc.send_line('G21 G91 ' + cmd)
                except:
                    print('Improper position command')

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
