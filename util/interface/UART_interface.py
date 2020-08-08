#!/usr/bin/env python3
"""Provides logging for the UART
"""

import serial
import threading
import time
import string


class UART_Interface:

    serial_timeout = 2
    line_timeout = 0.2

    # Initialize the UART
    def __init__(self, ser_port, ser_baud, logger):
        self.ser = serial.Serial(
            port=ser_port, baudrate=ser_baud, timeout=self.serial_timeout
        )

        self.logger = logger
        self.logger.info("UART Initialized on {}".format(ser_port))

        # Check if the port is open
        ser_status = "open" if self.ser.isOpen() else "closed"
        self.logger.info("Serial port is {}".format(ser_status))

        # Clear the serial to a clean state
        self.ser.flush()
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        # Setup thread variables
        self.read_thread = threading.Thread(target=self._free_run_read)
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self.continuous_read = False
        self.read_thread.start()

    # Get everything in serial buffer
    # UART reads from logic low, some magic is happening to get good input
    def readline_UART(self):
        my_lines = []
        line = b""
        timeout = time.time() + self.line_timeout

        while self.continuous_read and time.time() < timeout:
            out = self.ser.read(self.ser.inWaiting())
            out = out.replace(b"\x00", b"")

            if out != b"":
                timeout = time.time() + self.line_timeout
                line += out

        my_lines = line.split(b"\r\n")
        for i in my_lines:
            if i != b"":
                out = i.decode("utf-8", "ignore")
                my_str = "".join(x for x in out if x in string.printable)
                self.logger.info(my_str.strip())

    # Funtion for reading from UART
    def read_UART(self):
        with self.lock:
            if self.ser.inWaiting() > 0:
                self.readline_UART()

    # Function for writing to UART
    # TODO: make time.sleep non-blocking by moving to a new thread using Queue
    def write_UART(self, msg):
        with self.lock:
            self.ser.write("{}\r\n".format(msg))

    # Private function to read UART continuously
    def _free_run_read(self):
        while not self._stop_event.is_set():
            if self.continuous_read:
                self.read_UART()

    # Public function to read UART continuously
    def continuous_read_UART(self, continuous_read=True):
        self.continuous_read = continuous_read

    def is_real(self):
        return True

    # Cleanup
    def close(self):
        # Stop thread
        self.continuous_read = False
        self._stop_event.set()
        self.read_thread.join()

        # Close the serial port
        with self.lock:
            self.ser.close()
