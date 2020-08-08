#!/usr/bin/env python3
"""Provides logging for the Serial File
"""

import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Serial_File_Interface:

    # This is a handler to register with the filesystem observer
    class FileHandler(FileSystemEventHandler):
        def __init__(self, action):
            self._action = action

        def on_any_event(self, event):
            self._action(event)

    # Initialize the serial_file
    def __init__(self, serial_file, logger):

        self.logger = logger
        self.logger.info("UART Initialized on {}".format(serial_file))

        # Check if the port is open
        ser_status = "open" if os.path.exists(serial_file) else "closed"
        self.logger.info("Serial port is {}".format(ser_status))

        self.serial_file_path = serial_file
        self.ser_file = open(serial_file, "r", encoding="utf-8", errors="ignore")
        self.ser_file.seek(0, 2)  # Go to the end of the file

        self.event_handler = self.FileHandler(self.read_file_action)
        self.obs = Observer()
        self.obs.schedule(self.event_handler, path="./logs/", recursive=True)
        self.obs.start()

        # Setup thread variables
        self.lock = threading.Lock()

    def is_real(self):
        return False

    def read_file_action(self, event):
        e_path = os.path.normpath(event.src_path)
        if e_path == self.serial_file_path:
            self.read_file()

    # Funtion for reading from UART
    def read_file(self):
        with self.lock:
            # self.ser_file.seek(0, 2)
            # self.ser_file.seek(self.ser_file.tell() - 30, os.SEEK_SET) # assumes a line is fewer than 30 char
            # return_lines = self.ser_file.readlines()
            #line = return_lines[-1]+"\n" if return_lines else ""
            lines = self.ser_file.readlines()
            for line in lines:
                if line and line.strip() != "" and line.strip()[-1] != "\n":
                    line = line + "\n"
                    self.logger.info(line.strip())

    # Public function to read UART continuously
    def continuous_read_file(self, continuous_read=True):
        pass
    # Cleanup
    def close(self):
        # Close the serial port
        with self.lock:
            self.ser_file.close()
