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

# Open grbl serial port
s = serial.Serial('/dev/ttyACM0',115200)

# Open g-code file


# Wake up grbl
s.write("\r\n\r\n".encode())
time.sleep(2)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input

# Stream g-code to grb
class GRBL_Stream:

    def __init__(self, serial_port = '/dev/ttyACM0', baud_rate = 115200):

        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.feedrate = 100

        self.serial = serial.Serial(serial_port,baud_rate)

        self.init()

    def init(self):
        startup_file = open('startup.gcode','r');

        for line in startup_file:
            self.send_line(line)

    def set_feedrate(self, feedrate):
        self.feedrate = feedrate

    def get_feedrate(self):
        return self.feedrate

    def send_line(self, line):
        l = line.strip() # Strip all EOL characters for consistency
        print('Sending: ' + l)

        l = l + '\n'
        self.serial.write(l.encode()) # Send g-code block to grbl
        grbl_out_bytes = self.serial.readline() # Wait for grbl response with carriage return
        grbl_out = grbl_out_bytes.decode("UTF-8")

        print(' : ' + grbl_out.strip())


# Wait here until grbl is finished to close serial port and file.
def main():
    cnc = GRBL_Stream()

    while True:
        user_input = input('Input: ')
        if user_input == 'X' or user_input == 'Y':
            user_distance = input('Distance: ')
            try:
                cmd = user_input + user_distance + '.0 F' + cnc.get_feedrate()
                print(cmd)
                cnc.send_line('G21 G91 ' + cmd)
            except:
                print('Inproper command')
        elif user_input == 'F':
            user_feedrate = input('Feedrate: ')
            cnc.set_feedrate(user_feedrate)

if __name__ == "__main__":
    main()

# Close file and serial port
f.close()
s.close()
